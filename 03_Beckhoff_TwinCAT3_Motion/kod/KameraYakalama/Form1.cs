// ============================================================================
// KameraYakalama - Beckhoff IPC üzerinde çalışan WindowsFormsApp
// PLC'den gelen tetik sinyaliyle kameradan kare yakalar, sonucu PLC'ye yazar.
// NuGet: Beckhoff.TwinCAT.Ads, AForge.Video.DirectShow
// ============================================================================
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Windows.Forms;
using AForge.Video;
using AForge.Video.DirectShow;
using TwinCAT.Ads;

namespace KameraYakalama
{
    public partial class Form1 : Form
    {
        private readonly AdsClient _ads = new AdsClient();
        private VideoCaptureDevice _kamera;
        private Bitmap _sonKare;
        private readonly object _kilit = new object();
        private uint _tetikHandle;
        private const string KayitKlasoru = @"D:\Goruntuler";

        public Form1()
        {
            InitializeComponent();
            Directory.CreateDirectory(KayitKlasoru);
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            // 1) Kamerayı başlat
            var cihazlar = new FilterInfoCollection(FilterCategory.VideoInputDevice);
            if (cihazlar.Count == 0) { Log("Kamera bulunamadı"); return; }
            _kamera = new VideoCaptureDevice(cihazlar[0].MonikerString);
            _kamera.NewFrame += Kamera_NewFrame;
            _kamera.Start();

            // 2) TwinCAT PLC'ye bağlan (lokal, port 851)
            _ads.Connect(AmsNetId.Local, 851);
            _ads.AdsNotification += Ads_Notification;
            _tetikHandle = _ads.AddDeviceNotification(
                "GVL.bKameraTetik", sizeof(bool),
                new NotificationSettings(AdsTransMode.OnChange, 10, 0), null);
            Log("PLC bağlantısı kuruldu");
        }

        private void Kamera_NewFrame(object sender, NewFrameEventArgs e)
        {
            var kare = (Bitmap)e.Frame.Clone();
            lock (_kilit) { _sonKare?.Dispose(); _sonKare = kare; }
            pictureBox1.BeginInvoke((Action)(() =>
            {
                lock (_kilit)
                {
                    pictureBox1.Image?.Dispose();
                    pictureBox1.Image = (Bitmap)_sonKare.Clone();
                }
            }));
        }

        private void Ads_Notification(object sender, AdsNotificationEventArgs e)
        {
            if (e.Handle != _tetikHandle) return;
            bool tetik = e.Data.Span[0] != 0;
            if (!tetik) return;

            string dosya = Path.Combine(KayitKlasoru, $"img_{DateTime.Now:yyyyMMdd_HHmmss_fff}.jpg");
            bool basarili = false;
            lock (_kilit)
            {
                if (_sonKare != null) { _sonKare.Save(dosya, ImageFormat.Jpeg); basarili = true; }
            }
            _ads.WriteValue("GVL.bKameraTamam", basarili);
            BeginInvoke((Action)(() => Log(basarili ? $"Kaydedildi: {dosya}" : "Kare yok!")));
        }

        private void Log(string mesaj) =>
            listBox1.Items.Insert(0, $"{DateTime.Now:HH:mm:ss}  {mesaj}");

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            _kamera?.SignalToStop();
            if (_ads.IsConnected) _ads.DeleteDeviceNotification(_tetikHandle);
            _ads.Dispose();
            base.OnFormClosing(e);
        }
    }
}
