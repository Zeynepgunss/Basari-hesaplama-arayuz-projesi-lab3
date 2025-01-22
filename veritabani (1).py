import sqlite3

def db_connect():
    """Veritabanı bağlantısını oluşturur."""
    return sqlite3.connect("proje_db.sqlite")

def create_tables():
    """Gerekli tabloları oluşturur."""
    conn = db_connect()
    cursor = conn.cursor()

    # Dersler Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Dersler (
        ders_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ders_kodu TEXT NOT NULL,
        ders_adi TEXT NOT NULL
    )
    """)

    # Öğrenciler Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Ogrenciler (
        ogrenci_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ogrenci_no TEXT NOT NULL
    )
    """)

    # Ders-Öğrenci İlişkisi Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS DersOgrenci (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ders_id INTEGER NOT NULL,
        ogrenci_id INTEGER NOT NULL,
        FOREIGN KEY (ders_id) REFERENCES Dersler(ders_id) ON DELETE CASCADE,
        FOREIGN KEY (ogrenci_id) REFERENCES Ogrenciler(ogrenci_id) ON DELETE CASCADE
    )
    """)

    # Program Çıktıları Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ProgramCiktilari (
        prg_cikti_id INTEGER PRIMARY KEY AUTOINCREMENT,
        prg_cikti_no INTEGER NOT NULL,
        prg_cikti_adi TEXT NOT NULL
    )
    """)

    # Ders Çıktıları Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS DersCiktilari (
        ders_cikti_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ders_cikti_no INTEGER NOT NULL,
        prg_cikti_no INTEGER NOT NULL,
        ders_cikti_adi TEXT NOT NULL,
        FOREIGN KEY (prg_cikti_no) REFERENCES ProgramCiktilari(prg_cikti_no)
    )
    """)

    # Tablo 1
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Tablo1 (
        prg_cikti_no INTEGER NOT NULL,
        ders_cikti_no INTEGER NOT NULL,
        deger REAL NOT NULL,
        PRIMARY KEY (prg_cikti_no, ders_cikti_no),
        FOREIGN KEY (prg_cikti_no) REFERENCES ProgramCiktilari(prg_cikti_no),
        FOREIGN KEY (ders_cikti_no) REFERENCES DersCiktilari(ders_cikti_no)
    )
    """)

    # Tablo 2
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Tablo2 (
        ders_cikti_no INTEGER NOT NULL,
        kriter_adi TEXT NOT NULL,
        agirlik REAL NOT NULL,
        PRIMARY KEY (ders_cikti_no, kriter_adi),
        FOREIGN KEY (ders_cikti_no) REFERENCES DersCiktilari(ders_cikti_no)
    )
    """)



    # DegerlendirmeKriterleri Tablosu
    cursor.execute("""
       CREATE TABLE IF NOT EXISTS DegerlendirmeKriterleri (
           kriter_id INTEGER PRIMARY KEY AUTOINCREMENT,
           kriter TEXT NOT NULL,
           agirlik REAL NOT NULL
       )
       """)

    # Tablo Notlar
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS TabloNotlar (
        ogrenci_id INTEGER NOT NULL,
        ders_cikti_no INTEGER NOT NULL,
        odev1_notu REAL DEFAULT 0,
        odev2_notu REAL DEFAULT 0,
        quiz_notu REAL DEFAULT 0,
        vize_notu REAL DEFAULT 0,
        final_notu REAL DEFAULT 0,
        PRIMARY KEY (ogrenci_id, ders_cikti_no),
        FOREIGN KEY (ogrenci_id) REFERENCES Ogrenciler(ogrenci_id),
        FOREIGN KEY (ders_cikti_no) REFERENCES DersCiktilari(ders_cikti_no)
    )
    """)

    # Tablo 4 için geçici hesaplamaları saklayacak tablo
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Tablo4 (
        ogrenci_id INTEGER NOT NULL,
        ders_cikti_no INTEGER NOT NULL,
        toplam_not REAL DEFAULT 0,
        PRIMARY KEY (ogrenci_id, ders_cikti_no),
        FOREIGN KEY (ogrenci_id) REFERENCES Ogrenciler(ogrenci_id),
        FOREIGN KEY (ders_cikti_no) REFERENCES DersCiktilari(ders_cikti_no)
    )
    """)

    # Tablo 5 için geçici hesaplamaları saklayacak tablo
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Tablo5 (
        prg_cikti_no INTEGER NOT NULL,
        kriter_1 REAL DEFAULT 0,
        kriter_2 REAL DEFAULT 0,
        kriter_3 REAL DEFAULT 0,
        kriter_4 REAL DEFAULT 0,
        kriter_5 REAL DEFAULT 0,
        basari_orani REAL DEFAULT 0,
        PRIMARY KEY (prg_cikti_no),
        FOREIGN KEY (prg_cikti_no) REFERENCES ProgramCiktilari(prg_cikti_no)
    )
    """)




    conn.commit()
    conn.close()
    print("Tablolar başarıyla oluşturuldu!")

if __name__ == "__main__":
    create_tables()
