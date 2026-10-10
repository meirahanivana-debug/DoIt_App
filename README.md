# Doit — Build APK Android di GitHub Codespaces

Aplikasi ini dibuat dengan Kivy dan KivyMD. Versi KivyMD dikunci ke `1.2.0`
karena kode UI menggunakan API versi tersebut. Radius shadow KivyMD juga
ditetapkan sebagai empat nilai agar `BoxShadow` tidak menghentikan aplikasi
saat mulai dengan error `border_radius`. Tombol utama menggunakan subclass
yang memberi radius empat nilai sejak pembuatan widget, sebelum aturan KV
internal KivyMD membuat canvas. Lima gambar avatar yang dipakai halaman profil
juga disertakan di folder `avatars/`. Pillow dibutuhkan oleh import
`kivymd.uix.pickers` (color picker), walaupun aplikasi terutama memakai date
dan time picker. Tanpa Pillow, Python Android berhenti dengan
`ModuleNotFoundError: No module named 'PIL'` sebelum layar login dibuat.
Lencana profil dirender sebagai kartu ikon dan teks KivyMD dengan ukuran serta
warna eksplisit agar tidak berubah menjadi kotak kosong di Android. Avatar
profil memakai salah satu `avatars/avatar1.png` sampai `avatar5.png`; pilih
gambar di Edit Profil lalu tekan **SIMPAN PERUBAHAN** agar pilihan disimpan
dan diperbarui pada halaman Profil.

## Lencana dan pengingat deadline

Lencana dihitung dari jumlah tugas dan kebiasaan berstatus **Selesai** untuk
akun yang sedang masuk: Pemula (4), Konsisten (20), Produktif (50), dan
Master (100). Lencana yang belum dicapai ditampilkan abu-abu; setiap lencana
berubah warna segera setelah jumlah selesai memenuhi ambangnya.

Untuk tugas yang memiliki deadline mendatang, aplikasi menjadwalkan notifikasi
24 jam dan 1 jam sebelum deadline (hanya pengingat yang waktunya masih di masa
depan). Deadline tanggal saja dianggap jatuh tempo pukul 23.59. Pengingat
Android native tetap dijadwalkan saat aplikasi ditutup dan dipulihkan setelah
perangkat dinyalakan ulang. Mengedit deadline akan mengganti pengingat lama;
menyelesaikan atau menghapus tugas akan membatalkannya. Tugas baru yang
deadline-nya hari ini juga mengirim notifikasi langsung.

Izinkan DoIt mengirim notifikasi saat Android menampilkan permintaan izin.
Android 12 ke atas dapat menunda alarm yang tidak memiliki akses alarm presisi;
pengingat tetap memakai alarm yang diizinkan sistem, tetapi waktu tampilnya
dapat bergeser karena pengaturan baterai/Doze perangkat. Untuk waktu yang lebih
tepat, izinkan **Alarms & reminders / Alarm & pengingat** untuk DoIt di
pengaturan khusus aplikasi Android jika opsi tersebut tersedia.

## Build APK

Jalankan perintah berikut dari terminal Codespaces di direktori repositori:

```bash
sudo apt update
sudo apt install -y \
  git zip unzip ant openjdk-17-jdk \
  python3.12 python3.12-venv python3.12-dev \
  build-essential autoconf libtool pkg-config \
  zlib1g-dev libncurses-dev libtinfo6 cmake libffi-dev libssl-dev

python3.12 -m venv .venv-build
source .venv-build/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install "Cython==0.29.37" "buildozer==1.5.0"

# Pilih JDK 17 untuk Android Gradle Plugin.
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH="$JAVA_HOME/bin:$PATH"

# Bersihkan hasil build sebelumnya, terutama setelah mengganti versi library.
buildozer android clean

# Build APK debug yang dapat dipasang untuk pengujian.
buildozer -v android debug
```

Buildozer akan mengunduh Android SDK/NDK dan dependensi build pada build
pertama. Terima lisensi Android SDK jika diminta. Setelah build berhasil, APK
tersimpan di direktori `bin/`. Periksa nama file yang dihasilkan dengan:

```bash
ls -lh bin/*.apk
```

Unduh APK dari panel Explorer Codespaces (`bin/`), pindahkan ke perangkat
Android, lalu buka APK untuk memasangnya. Android mungkin meminta izin untuk menginstal aplikasi dari sumber tersebut.
Pastikan memasang APK baru dari `bin/`, bukan membuka lagi APK lama yang sudah
ada di ponsel. Versi `0.8` mencakup lencana dinamis dan pengingat deadline
native. Jika pembaruan ditolak,
hapus versi lama lalu pasang APK baru. Menghapus aplikasi juga menghapus data
lokal aplikasi.

Jika build berhenti karena lisensi Android SDK belum diterima, jalankan
perintah berikut setelah Buildozer selesai mengunduh SDK, lalu ulangi build:

```bash
yes | "$HOME/.buildozer/android/platform/android-sdk/tools/bin/sdkmanager" \
  --sdk_root="$HOME/.buildozer/android/platform/android-sdk" --licenses
buildozer -v android debug
```

## Build ulang

Aktifkan kembali environment Python sebelum menjalankan perintah build:

```bash
source .venv-build/bin/activate
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH="$JAVA_HOME/bin:$PATH"
buildozer -v android debug
```

Jika mengubah versi dependensi atau konfigurasi Buildozer, bersihkan hasil
build aplikasi (jangan hapus seluruh folder `.buildozer`, karena isinya SDK/NDK
yang sudah diunduh) terlebih dahulu:

```bash
buildozer android clean
buildozer -v android debug
```

Jika aplikasi tetap tertutup setelah presplash, build APK yang sukses belum
cukup untuk menentukan penyebab crash di perangkat. Aktifkan USB debugging,
sambungkan ponsel ke komputer yang memiliki Android Platform Tools, lalu ambil
log saat membuka aplikasi:

```bash
adb logcat -c
adb shell monkey -p org.doit.doitapp 1
adb logcat -d -v time | grep -iE 'AndroidRuntime|FATAL EXCEPTION|Traceback|python|kivy|SDL|doitapp'
```

Kirim bagian log yang memuat `FATAL EXCEPTION`, `Traceback`, atau error pertama
setelah aplikasi dibuka. Codespace tanpa perangkat/emulator Android tidak dapat
menghasilkan log runtime Android tersebut.
