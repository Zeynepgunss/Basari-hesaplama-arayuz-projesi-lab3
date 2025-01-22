import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from veritabani import db_connect, create_tables

# Ders Ekleme İşlemleri
def open_ders_window():
    def add_ders_to_students():
        ders_kodu = ders_kodu_entry.get()
        ders_adi = ders_adi_entry.get()
        selected_students = [student_listbox.get(idx) for idx in student_listbox.curselection()]
        all_students = select_all_var.get()  # Tüm öğrencilere ekleme seçeneği

        if not ders_kodu or not ders_adi:
            messagebox.showwarning("Hata", "Lütfen tüm alanları doldurun!")
            return

        if not selected_students and not all_students:
            messagebox.showwarning("Hata", "Lütfen öğrenci(ler) seçin veya tüm öğrencilere eklemeyi seçin!")
            return

        try:
            conn = db_connect()
            cursor = conn.cursor()

            # Dersi "Dersler" tablosuna ekle
            cursor.execute("INSERT OR IGNORE INTO Dersler (ders_kodu, ders_adi) VALUES (?, ?)", (ders_kodu, ders_adi))

            # Dersin ID'sini al
            cursor.execute("SELECT ders_id FROM Dersler WHERE ders_kodu = ?", (ders_kodu,))
            ders_id = cursor.fetchone()[0]

            # Öğrencilere dersi ekle
            if all_students:
                cursor.execute("SELECT ogrenci_id FROM Ogrenciler")
                all_student_ids = [row[0] for row in cursor.fetchall()]
                for ogrenci_id in all_student_ids:
                    cursor.execute("INSERT OR IGNORE INTO DersOgrenci (ders_id, ogrenci_id) VALUES (?, ?)", (ders_id, ogrenci_id))
            else:
                for student in selected_students:
                    ogrenci_no = student.split(" - ")[0]  # Öğrenci numarasını al
                    cursor.execute("SELECT ogrenci_id FROM Ogrenciler WHERE ogrenci_no = ?", (ogrenci_no,))
                    ogrenci_id = cursor.fetchone()[0]
                    cursor.execute("INSERT OR IGNORE INTO DersOgrenci (ders_id, ogrenci_id) VALUES (?, ?)", (ders_id, ogrenci_id))

            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Ders başarıyla öğrencilere eklendi!")
            ders_kodu_entry.delete(0, tk.END)
            ders_adi_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu: {e}")

    def load_student_list():
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT ogrenci_no FROM Ogrenciler")  # Sadece öğrenci numaralarını al
            students = cursor.fetchall()
            conn.close()

            for ogrenci_no in students:
                student_listbox.insert(tk.END, ogrenci_no[0])  # Sadece öğrenci_no'yu göster
        except Exception as e:
            messagebox.showerror("Hata", f"Öğrenci listesi yüklenirken bir hata oluştu: {e}")

    ders_window = tk.Toplevel(root)
    ders_window.title("Ders Ekleme")
    ders_window.geometry("600x400")

    tk.Label(ders_window, text="Ders Kodu:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    ders_kodu_entry = tk.Entry(ders_window)
    ders_kodu_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(ders_window, text="Ders Adı:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    ders_adi_entry = tk.Entry(ders_window)
    ders_adi_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(ders_window, text="Öğrenci Seçin:").grid(row=2, column=0, padx=5, pady=5, sticky="nw")
    student_listbox = tk.Listbox(ders_window, selectmode="multiple", height=10, width=40)
    student_listbox.grid(row=2, column=1, padx=5, pady=5)

    select_all_var = tk.IntVar()
    tk.Checkbutton(ders_window, text="Tüm öğrencilere ekle", variable=select_all_var).grid(row=3, column=1, sticky="w", padx=5, pady=5)

    tk.Button(ders_window, text="Dersi Ekle", command=add_ders_to_students).grid(row=4, column=0, columnspan=2, pady=10)
    tk.Button(ders_window, text="Kapat", command=ders_window.destroy).grid(row=5, column=0, columnspan=2, pady=5)

    # Öğrenci listesini yükle
    load_student_list()


def open_ders_ogrenci_window():
    def load_ders_ogrenci_list():
        """Seçilen dersin öğrenci listesini yükler."""
        selected_item = ders_listbox.curselection()
        if not selected_item:
            messagebox.showwarning("Uyarı", "Lütfen bir ders seçin!")
            return

        ders_kodu = ders_listbox.get(selected_item[0]).split(" - ")[0]

        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("""
            SELECT D.ders_kodu, D.ders_adi, O.ogrenci_no
            FROM DersOgrenci DO
            JOIN Dersler D ON DO.ders_id = D.ders_id
            JOIN Ogrenciler O ON DO.ogrenci_id = O.ogrenci_id
            WHERE D.ders_kodu = ?;
            """, (ders_kodu,))
            results = cursor.fetchall()
            conn.close()

            # Listeyi temizleyip yeni verileri ekle
            ogrenci_listbox.delete(0, tk.END)
            for row in results:
                ogrenci_listbox.insert(tk.END, f"Öğrenci No: {row[2]}")
        except Exception as e:
            messagebox.showerror("Hata", f"Öğrenci listesi yüklenirken hata oluştu: {e}")

    ders_ogrenci_window = tk.Toplevel(root)
    ders_ogrenci_window.title("Ders ve Öğrenci Listesi")
    ders_ogrenci_window.geometry("600x400")

    tk.Label(ders_ogrenci_window, text="Ders Listesi:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    ders_listbox = tk.Listbox(ders_ogrenci_window, height=10, width=40)
    ders_listbox.grid(row=1, column=0, padx=5, pady=5)

    tk.Label(ders_ogrenci_window, text="Öğrenci Listesi:").grid(row=0, column=1, padx=5, pady=5, sticky="w")
    ogrenci_listbox = tk.Listbox(ders_ogrenci_window, height=10, width=40)
    ogrenci_listbox.grid(row=1, column=1, padx=5, pady=5)

    tk.Button(ders_ogrenci_window, text="Öğrenci Listesini Göster", command=load_ders_ogrenci_list).grid(row=2,
                                                                                                         column=0,
                                                                                                         columnspan=2,
                                                                                                         pady=10)

    # Dersleri listeye yükle
    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT ders_kodu, ders_adi FROM Dersler")
        dersler = cursor.fetchall()
        conn.close()

        for ders in dersler:
            ders_listbox.insert(tk.END, f"{ders[0]} - {ders[1]}")
    except Exception as e:
        messagebox.showerror("Hata", f"Ders listesi yüklenirken hata oluştu: {e}")


# Öğrenci Listesi Yükleme İşlemleri
def open_ogrenci_window():
    def load_ogrenciler():
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if not file_path:
            return

        try:
            df = pd.read_excel(file_path)
            conn = db_connect()
            cursor = conn.cursor()
            for _, row in df.iterrows():
                cursor.execute("INSERT INTO Ogrenciler (ogrenci_no) VALUES (?)", (row["Öğrenci No"],))
            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Öğrenci listesi başarıyla yüklendi!")
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu: {e}")

    ogrenci_window = tk.Toplevel(root)
    ogrenci_window.title("Öğrenci Listesi Yükleme")
    ogrenci_window.geometry("400x150")

    tk.Button(ogrenci_window, text="Excel'den Yükle", command=load_ogrenciler).pack(pady=20)
    tk.Button(ogrenci_window, text="Kapat", command=ogrenci_window.destroy).pack()
# Değerlendirme Kriterleri İşlemleri
def open_criteria_window():
    def load_criteria_to_list():
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT kriter_id, kriter, agirlik FROM DegerlendirmeKriterleri")
        kriterler = cursor.fetchall()
        conn.close()

        kriter_list.delete(*kriter_list.get_children())
        for kriter_id, kriter, agirlik in kriterler:
            kriter_list.insert("", "end", values=(kriter_id, kriter, agirlik))

    def add_criteria():
        kriter = kriter_combobox.get()
        agirlik = agirlik_entry.get()

        if not kriter or not agirlik:
            messagebox.showwarning("Eksik Bilgi", "Lütfen kriter ve ağırlık değerlerini girin!")
            return

        try:
            agirlik = float(agirlik)
            if agirlik < 0 or agirlik > 100:
                messagebox.showerror("Hatalı Değer", "Ağırlık 0 ile 100 arasında olmalıdır!")
                return
        except ValueError:
            messagebox.showerror("Hatalı Değer", "Ağırlık bir sayı olmalıdır!")
            return

        current_weight = get_total_weight()
        if current_weight + agirlik > 100:
            messagebox.showerror("Ağırlık Hatası", f"Ağırlık toplamı {current_weight + agirlik}. 100'ü geçemez!")
            return

        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO DegerlendirmeKriterleri (kriter, agirlik) VALUES (?, ?)", (kriter, agirlik))
        conn.commit()
        conn.close()

        kriter_combobox.set("")
        agirlik_entry.delete(0, tk.END)
        load_criteria_to_list()
        messagebox.showinfo("Başarılı", f"{kriter} kriteri başarıyla eklendi!")

    def delete_selected_criteria():
        selected_item = kriter_list.selection()
        if not selected_item:
            messagebox.showwarning("Seçim Yok", "Lütfen silmek istediğiniz bir kriteri seçin!")
            return

        try:
            selected_values = kriter_list.item(selected_item[0])['values']
            kriter_id = selected_values[0]

            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM DegerlendirmeKriterleri WHERE kriter_id = ?", (kriter_id,))
            conn.commit()
            conn.close()

            load_criteria_to_list()
            messagebox.showinfo("Başarılı", "Kriter başarıyla silindi!")
        except Exception as e:
            messagebox.showerror("Hata", f"Kriter silinirken bir hata oluştu: {e}")

    def edit_selected_criteria():
        selected_item = kriter_list.selection()
        if not selected_item:
            messagebox.showwarning("Seçim Yok", "Lütfen düzenlemek istediğiniz bir kriteri seçin!")
            return

        try:
            selected_values = kriter_list.item(selected_item[0])['values']
            kriter_id = selected_values[0]
            yeni_agirlik = float(agirlik_entry.get())

            if not (0 <= yeni_agirlik <= 100):
                messagebox.showerror("Hata", "Ağırlık 0 ile 100 arasında olmalıdır!")
                return

            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("UPDATE DegerlendirmeKriterleri SET agirlik = ? WHERE kriter_id = ?", (yeni_agirlik, kriter_id))
            conn.commit()
            conn.close()

            agirlik_entry.delete(0, tk.END)
            load_criteria_to_list()
            messagebox.showinfo("Başarılı", "Kriter başarıyla güncellendi!")
        except Exception as e:
            messagebox.showerror("Hata", f"Kriter güncellenirken bir hata oluştu: {e}")

    def get_total_weight():
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(agirlik) FROM DegerlendirmeKriterleri")
        total_weight = cursor.fetchone()[0]
        conn.close()
        return total_weight or 0

    criteria_window = tk.Toplevel(root)
    criteria_window.title("Değerlendirme Kriterleri")
    criteria_window.geometry("600x500")

    tk.Label(criteria_window, text="Kriter:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    kriter_combobox = ttk.Combobox(criteria_window, state="readonly", values=["Ödev", "Proje", "Sunum", "Rapor", "KPL", "Derse Katılım", "Vize", "Final"])
    kriter_combobox.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(criteria_window, text="Ağırlık (%):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    agirlik_entry = tk.Entry(criteria_window)
    agirlik_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Button(criteria_window, text="Ekle", command=add_criteria).grid(row=2, column=0, columnspan=2, pady=10)

    kriter_list = ttk.Treeview(criteria_window, columns=("ID", "Kriter", "Ağırlık"), show="headings", height=10)
    kriter_list.heading("ID", text="ID")
    kriter_list.heading("Kriter", text="Kriter")
    kriter_list.heading("Ağırlık", text="Ağırlık (%)")
    kriter_list.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

    tk.Button(criteria_window, text="Seçili Kriteri Sil", command=delete_selected_criteria).grid(row=4, column=0, pady=5)
    tk.Button(criteria_window, text="Seçili Kriteri Düzenle", command=edit_selected_criteria).grid(row=4, column=1, pady=5)
    tk.Button(criteria_window, text="Kapat", command=criteria_window.destroy).grid(row=5, column=0, columnspan=2, pady=10)

    load_criteria_to_list()

# Tablo 1 işlemleri için yeni pencere
def open_tablo1_window():
    def add_tablo1_entry():
        """Elle veri ekleme."""
        prg_cikti_no = prg_cikti_entry.get()
        ders_cikti_no = ders_cikti_entry.get()
        deger = deger_entry.get()

        try:
            prg_cikti_no = int(prg_cikti_no)
            ders_cikti_no = int(ders_cikti_no)
            deger = float(deger)

            if not (0 <= deger <= 1):
                messagebox.showerror("Hata", "[0, 1] aralığında bir değer girilmelidir!")
                return

            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Tablo1 (prg_cikti_no, ders_cikti_no, deger) VALUES (?, ?, ?)",
                (prg_cikti_no, ders_cikti_no, deger)
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", "Tablo 1 kaydı başarıyla eklendi!")
            load_data_to_list()  # Listeyi güncelle
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir sayı değeri girilmelidir!")
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu: {e}")

    def load_tablo1_from_excel():
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if not file_path:
            return

        try:
            # Excel dosyasını oku
            df = pd.read_excel(file_path)

            # Gerekli sütunları kontrol et
            expected_columns = ["Prg Çıktı", "1", "2", "3", "4", "5", "İlişki Değ."]
            for col in expected_columns:
                if col not in df.columns:
                    messagebox.showerror("Hata", f"Excel dosyasında '{col}' sütunu bulunamadı!")
                    return

            # Değerlerin [0, 1] aralığında olup olmadığını kontrol et
            for col in df.columns[1:-1]:  # "Prg Çıktı" ve "İlişki Değ." hariç
                if not df[col].between(0, 1).all():
                    messagebox.showerror("Hata", f"'{col}' sütununda [0, 1] aralığı dışında değerler var!")
                    return

            # Veritabanına ekle
            conn = db_connect()
            cursor = conn.cursor()

            for _, row in df.iterrows():
                prg_cikti_no = int(row["Prg Çıktı"])

                for ders_cikti_no, deger in enumerate(row[1:-1], start=1):  # "İlişki Değ." hariç sütunlar
                    cursor.execute(
                        "INSERT INTO Tablo1 (prg_cikti_no, ders_cikti_no, deger) VALUES (?, ?, ?)",
                        (prg_cikti_no, ders_cikti_no, deger)
                    )

            conn.commit()
            conn.close()
            load_data_to_list()  # Listeyi güncelle
            messagebox.showinfo("Başarılı", "Tablo 1 başarıyla yüklendi!")
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu: {e}")

    def load_data_to_list():
        """Veritabanından verileri listeye yükle."""
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT prg_cikti_no, ders_cikti_no, deger FROM Tablo1")
        rows = cursor.fetchall()
        conn.close()

        # Listeyi temizle ve yeni verileri ekle
        tablo1_list.delete(*tablo1_list.get_children())
        for row in rows:
            tablo1_list.insert("", "end", values=row)

    def delete_selected_entry():
        """Seçili kaydı sil."""
        selected_item = tablo1_list.selection()
        if not selected_item:
            messagebox.showwarning("Seçim Yok", "Lütfen silmek istediğiniz bir kaydı seçin!")
            return

        try:
            conn = db_connect()
            cursor = conn.cursor()
            for item in selected_item:
                selected_values = tablo1_list.item(item)['values']
                prg_cikti_no = selected_values[0]
                ders_cikti_no = selected_values[1]

                # Veritabanından sil
                cursor.execute(
                    "DELETE FROM Tablo1 WHERE prg_cikti_no = ? AND ders_cikti_no = ?",
                    (prg_cikti_no, ders_cikti_no)
                )

            conn.commit()
            conn.close()
            load_data_to_list()  # Listeyi güncelle
            messagebox.showinfo("Başarılı", "Seçili kayıtlar başarıyla silindi!")
        except Exception as e:
            messagebox.showerror("Hata", f"Kayıt silinirken bir hata oluştu: {e}")

    tablo1_window = tk.Toplevel(root)
    tablo1_window.title("Tablo 1 İşlemleri")
    tablo1_window.geometry("800x500")

    # Elle giriş alanları
    tk.Label(tablo1_window, text="Prg Çıktı No:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    prg_cikti_entry = tk.Entry(tablo1_window)
    prg_cikti_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(tablo1_window, text="Ders Çıktı No:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    ders_cikti_entry = tk.Entry(tablo1_window)
    ders_cikti_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(tablo1_window, text="Değer:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    deger_entry = tk.Entry(tablo1_window)
    deger_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Button(tablo1_window, text="Ekle", command=add_tablo1_entry).grid(row=3, column=0, columnspan=2, pady=10)

    tk.Button(tablo1_window, text="Excel'den Yükle", command=load_tablo1_from_excel).grid(row=4, column=0, columnspan=2, pady=5)

    # Tablo 1'deki verileri listeleme alanı
    tablo1_list = ttk.Treeview(tablo1_window, columns=("Prg Çıktı No", "Ders Çıktı No", "Değer"), show="headings", height=15)
    tablo1_list.heading("Prg Çıktı No", text="Prg Çıktı No")
    tablo1_list.heading("Ders Çıktı No", text="Ders Çıktı No")
    tablo1_list.heading("Değer", text="Değer")
    tablo1_list.grid(row=5, column=0, columnspan=2, padx=5, pady=10)

    tk.Button(tablo1_window, text="Seçili Kayıtları Sil", command=delete_selected_entry).grid(row=6, column=0, columnspan=2, pady=10)

    tk.Button(tablo1_window, text="Kapat", command=tablo1_window.destroy).grid(row=7, column=0, columnspan=2, pady=10)

    # İlk yükleme
    load_data_to_list()


def create_dynamic_tablo2():
    """Tablo2'yi dinamik olarak oluşturur."""
    try:
        conn = db_connect()
        cursor = conn.cursor()

        # DegerlendirmeKriterleri tablosundaki kriterleri al
        cursor.execute("SELECT kriter FROM DegerlendirmeKriterleri")
        kriterler = [row[0] for row in cursor.fetchall()]

        # Eski Tablo2 varsa sil
        cursor.execute("DROP TABLE IF EXISTS Tablo2")

        # Yeni Tablo2'yi oluştur
        columns = ", ".join([f"{kriter} REAL DEFAULT 0" for kriter in kriterler])
        query = f"""
        CREATE TABLE Tablo2 (
            ders_cikti_no INTEGER NOT NULL,
            {columns}
        )
        """
        cursor.execute(query)
        conn.commit()
        conn.close()
        print("Tablo2 başarıyla oluşturuldu!")
    except Exception as e:
        print(f"Tablo2 oluşturulurken bir hata oluştu: {e}")

def open_tablo2_window():
    """Tablo2 işlemleri için yeni bir pencere açar."""

    def load_criteria():
        """Değerlendirme kriterlerini veritabanından alır."""
        nonlocal kriter_list  # Kriter listesi dinamik olarak kullanılacak
        kriter_list = []
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT kriter, agirlik FROM DegerlendirmeKriterleri")
            kriter_list = cursor.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror("Hata", f"Değerlendirme kriterleri alınırken bir hata oluştu: {e}")

    def add_tablo2_entry():
        """Yeni bir Tablo2 girdisi ekler."""
        try:
            ders_cikti_no = int(ders_cikti_entry.get())
            kriter_values = [float(entry.get()) for entry in kriter_entries]

            if not all(0 <= value <= 1 for value in kriter_values):
                messagebox.showerror("Hata", "Kriter değerleri [0, 1] aralığında olmalıdır!")
                return

            conn = db_connect()
            cursor = conn.cursor()
            placeholders = ", ".join(["?"] * len(kriter_values))
            query = f"INSERT INTO Tablo2 (ders_cikti_no, {', '.join([k[0] for k in kriter_list])}) VALUES (?, {placeholders})"
            cursor.execute(query, [ders_cikti_no] + kriter_values)
            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", "Tablo 2 kaydı başarıyla eklendi!")
            load_data_to_list()
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu: {e}")

    def load_data_to_list():
        """Tablo2 verilerini yükler."""
        try:
            conn = db_connect()
            cursor = conn.cursor()
            columns = ["ders_cikti_no"] + [k[0] for k in kriter_list]
            cursor.execute(f"SELECT {', '.join(columns)} FROM Tablo2")
            rows = cursor.fetchall()
            conn.close()

            tablo2_list.delete(*tablo2_list.get_children())
            for row in rows:
                tablo2_list.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Hata", f"Veriler yüklenirken bir hata oluştu: {e}")

    # Pencere başlatma
    tablo2_window = tk.Toplevel(root)
    tablo2_window.title("Tablo 2 İşlemleri")
    tablo2_window.geometry("900x600")

    # Kriterleri yükle
    kriter_list = []
    load_criteria()

    # Girdi alanları
    tk.Label(tablo2_window, text="Ders Çıktı No:").grid(row=0, column=0, padx=5, pady=5)
    ders_cikti_entry = tk.Entry(tablo2_window)
    ders_cikti_entry.grid(row=0, column=1, padx=5, pady=5)

    # Dinamik kriter girdileri
    kriter_entries = []
    for i, (kriter, _) in enumerate(kriter_list):
        tk.Label(tablo2_window, text=f"{kriter}:").grid(row=i + 1, column=0, padx=5, pady=5)
        entry = tk.Entry(tablo2_window)
        entry.grid(row=i + 1, column=1, padx=5, pady=5)
        kriter_entries.append(entry)

    # Ekleme butonu
    tk.Button(tablo2_window, text="Ekle", command=add_tablo2_entry).grid(row=len(kriter_list) + 1, column=0, columnspan=2, pady=10)

    # Treeview
    columns = ["Ders Çıktı No"] + [k[0] for k in kriter_list]
    tablo2_list = ttk.Treeview(tablo2_window, columns=columns, show="headings", height=15)
    tablo2_list.grid(row=len(kriter_list) + 3, column=0, columnspan=2, padx=5, pady=10)
    for kriter, agirlik in [("Ders Çıktı No", "")] + kriter_list:
        tablo2_list.heading(kriter, text=f"{kriter} (%{agirlik})" if agirlik else kriter)

    # Verileri yükle
    load_data_to_list()

    # Kapat butonu
    tk.Button(tablo2_window, text="Kapat", command=tablo2_window.destroy).grid(row=len(kriter_list) + 4, column=0, columnspan=2, pady=10)


# Öncelikle Tablo2'yi oluştur
create_dynamic_tablo2()

def open_tablo_notlar_window():
    def add_tablo_notlar_entry():
        ogrenci_no = ogrenci_no_entry.get()
        ders_cikti_no = ders_cikti_no_entry.get()
        not_degeri = not_degeri_entry.get()

        try:
            # Girdileri kontrol et
            ogrenci_no = int(ogrenci_no)
            ders_cikti_no = int(ders_cikti_no)
            not_degeri = float(not_degeri)

            if not (0 <= not_degeri <= 100):
                messagebox.showerror("Hata", "Not değeri 0 ile 100 arasında olmalıdır!")
                return

            # Veritabanına ekle
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO TabloNotlar (ogrenci_no, ders_cikti_no, not_degeri) VALUES (?, ?, ?)",
                (ogrenci_no, ders_cikti_no, not_degeri)
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", "Not başarıyla eklendi!")
            load_data_to_list()  # Listeyi güncelle
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir sayı değeri girilmelidir!")
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu: {e}")

    def load_data_to_list():
        """Veritabanındaki verileri tabloya yükle."""
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT ogrenci_no, ders_cikti_no, not_degeri FROM TabloNotlar")
        rows = cursor.fetchall()
        conn.close()

        # Listeyi temizle ve yeni verileri ekle
        tablo_notlar_list.delete(*tablo_notlar_list.get_children())
        for row in rows:
            tablo_notlar_list.insert("", "end", values=row)

    def load_from_excel():
        """Excel'den verileri yükle."""
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if not file_path:
            return

        try:
            # Excel dosyasını oku
            df = pd.read_excel(file_path)

            # Gerekli sütunların varlığını kontrol et
            if "Öğrenci No" not in df.columns or "Ders Çıktı No" not in df.columns or "Not" not in df.columns:
                messagebox.showerror("Hata", "Excel dosyası uygun formatta değil!")
                return

            # Veritabanına ekle
            conn = db_connect()
            cursor = conn.cursor()
            for _, row in df.iterrows():
                cursor.execute(
                    "INSERT INTO TabloNotlar (ogrenci_no, ders_cikti_no, not_degeri) VALUES (?, ?, ?)",
                    (row["Öğrenci No"], row["Ders Çıktı No"], row["Not"])
                )
            conn.commit()
            conn.close()
            messagebox.showinfo("Başarılı", "Excel başarıyla yüklendi!")
            load_data_to_list()
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu: {e}")

    tablo_notlar_window = tk.Toplevel(root)
    tablo_notlar_window.title("Tablo Notlar İşlemleri")
    tablo_notlar_window.geometry("600x400")

    tk.Label(tablo_notlar_window, text="Öğrenci No:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    ogrenci_no_entry = tk.Entry(tablo_notlar_window)
    ogrenci_no_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(tablo_notlar_window, text="Ders Çıktı No:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    ders_cikti_no_entry = tk.Entry(tablo_notlar_window)
    ders_cikti_no_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(tablo_notlar_window, text="Not:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    not_degeri_entry = tk.Entry(tablo_notlar_window)
    not_degeri_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Button(tablo_notlar_window, text="Ekle", command=add_tablo_notlar_entry).grid(row=3, column=0, columnspan=2, pady=10)
    tk.Button(tablo_notlar_window, text="Excel'den Yükle", command=load_from_excel).grid(row=4, column=0, columnspan=2, pady=5)

    # Treeview ile listeleme
    tablo_notlar_list = ttk.Treeview(tablo_notlar_window, columns=("Öğrenci No", "Ders Çıktı No", "Not"), show="headings", height=10)
    tablo_notlar_list.heading("Öğrenci No", text="Öğrenci No")
    tablo_notlar_list.heading("Ders Çıktı No", text="Ders Çıktı No")
    tablo_notlar_list.heading("Not", text="Not")
    tablo_notlar_list.grid(row=5, column=0, columnspan=2, padx=5, pady=10, sticky="nsew")

    load_data_to_list()


def generate_tablo4():
    """Tablo 4 verilerini oluştur ve bir Excel dosyasına kaydet."""
    try:
        conn = db_connect()
        cursor = conn.cursor()

        # Öğrencilerin notları ve ağırlıkları ile ilgili tüm verileri al
        cursor.execute("""
            SELECT 
                TabloNotlar.ders_cikti_no, 
                TabloNotlar.ogrenci_no, 
                TabloNotlar.odev1_notu, 
                TabloNotlar.odev2_notu, 
                TabloNotlar.quiz_notu, 
                TabloNotlar.vize_notu, 
                TabloNotlar.final_notu, 
                DegerlendirmeKriterleri.odev1_agirlik, 
                DegerlendirmeKriterleri.odev2_agirlik, 
                DegerlendirmeKriterleri.quiz_agirlik, 
                DegerlendirmeKriterleri.vize_agirlik, 
                DegerlendirmeKriterleri.final_agirlik
            FROM TabloNotlar
            JOIN DegerlendirmeKriterleri 
            ON TabloNotlar.ders_cikti_no = DegerlendirmeKriterleri.ders_cikti_no
        """)
        data = cursor.fetchall()
        conn.close()

        if not data:
            messagebox.showwarning("Uyarı", "Tablo 4 için veri bulunamadı!")
            return

        # Tablo 4 sütunlarını oluştur
        columns = [
            "Ders Çıktı", "Ödev1", "Ödev2", "Quiz", "Vize", "Final",
            "TOPLAM", "MAX", "%Başarı"
        ]
        df = pd.DataFrame(columns=columns)

        for row in data:
            ders_cikti_no = row[0]
            ogrenci_no = row[1]
            odev1 = row[2] * row[7] / 100
            odev2 = row[3] * row[8] / 100
            quiz = row[4] * row[9] / 100
            vize = row[5] * row[10] / 100
            final = row[6] * row[11] / 100
            toplam = round(odev1 + odev2 + quiz + vize + final, 1)
            max_puan = 20 + 70 + 80  # Örnek: Maksimum puanların toplamı
            basari_yuzdesi = round((toplam / max_puan) * 100, 2)

            # Satırı Tablo 4 formatına uygun ekle
            df = pd.concat([df, pd.DataFrame.from_records([{
                "Ders Çıktı": ders_cikti_no,
                "Ödev1": round(odev1, 1),
                "Ödev2": round(odev2, 1),
                "Quiz": round(quiz, 1),
                "Vize": round(vize, 1),
                "Final": round(final, 1),
                "TOPLAM": toplam,
                "MAX": max_puan,
                "%Başarı": basari_yuzdesi
            }])])

        # Excel dosyasına kaydet
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return

        with pd.ExcelWriter(file_path) as writer:
            df.to_excel(writer, index=False, sheet_name="Tablo 4")
        messagebox.showinfo("Başarılı", "Tablo 4 başarıyla oluşturuldu ve kaydedildi!")
    except Exception as e:
        messagebox.showerror("Hata", f"Tablo 4 oluşturulurken bir hata oluştu: {e}")

def create_tablo5():
    """
    Tablo 5 verilerini hesaplar ve Excel dosyası olarak kaydeder.
    """
    try:
        # Veritabanı bağlantısı
        conn = db_connect()
        cursor = conn.cursor()

        # Program çıktıları alınır
        cursor.execute("SELECT prg_cikti_no FROM ProgramCiktilari")
        program_ciktilari = cursor.fetchall()

        # Ders çıktıları alınır
        cursor.execute("SELECT prg_cikti_no, ders_cikti_no FROM DersCiktilari")
        ders_ciktilari = cursor.fetchall()

        # TabloNotlar'dan notlar alınır
        cursor.execute("""
        SELECT tn.ders_cikti_no, tn.odev1_notu, tn.odev2_notu, tn.quiz_notu, 
               tn.vize_notu, tn.final_notu, dc.prg_cikti_no
        FROM TabloNotlar tn
        INNER JOIN DersCiktilari dc ON tn.ders_cikti_no = dc.ders_cikti_no
        """)
        notlar = cursor.fetchall()

        # Tablo 5'in veri yapısını oluştur
        tablo5_data = []

        for prg_cikti in program_ciktilari:
            prg_cikti_no = prg_cikti[0]
            ilgili_dersler = [ders for ders in ders_ciktilari if ders[0] == prg_cikti_no]

            kriter_notlari = {i: 0 for i in range(1, 6)}  # Kriterler için varsayılan değerler
            basari_orani = 0
            toplam_katki = 0

            for ders_cikti in ilgili_dersler:
                ders_cikti_no = ders_cikti[1]

                # İlgili ders çıktısına ait notları al
                ders_notlari = [not_row for not_row in notlar if not_row[0] == ders_cikti_no]

                for not_row in ders_notlari:
                    odev1, odev2, quiz, vize, final, prg_cikti_no = not_row[1:]
                    toplam_not = odev1 + odev2 + quiz + vize + final
                    toplam_katki += toplam_not

                    # Kriterlere göre notları ekle
                    kriter_notlari[1] += odev1
                    kriter_notlari[2] += odev2
                    kriter_notlari[3] += quiz
                    kriter_notlari[4] += vize
                    kriter_notlari[5] += final

            # Başarı oranını hesapla
            if toplam_katki > 0:
                basari_orani = toplam_katki / (len(ilgili_dersler) * 100) * 100

            # Tablo 5 satırını oluştur
            tablo5_data.append([
                prg_cikti_no,
                kriter_notlari[1],
                kriter_notlari[2],
                kriter_notlari[3],
                kriter_notlari[4],
                kriter_notlari[5],
                round(basari_orani, 2)
            ])

        # Excel dosyasına yaz
        import pandas as pd

        tablo5_df = pd.DataFrame(
            tablo5_data,
            columns=["Prg Çıktı", "1", "2", "3", "4", "5", "Başarı Oranı"]
        )
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if file_path:
            tablo5_df.to_excel(file_path, index=False)
            messagebox.showinfo("Başarılı", f"Tablo 5 başarıyla oluşturuldu ve {file_path} olarak kaydedildi!")

    except Exception as e:
        messagebox.showerror("Hata", f"Tablo 5 oluşturulurken bir hata oluştu: {e}")

    finally:
        if conn:
            conn.close()
# Ana Menü
root = tk.Tk()
root.title("Ana Menü")
root.geometry("300x400")

# Ana menüdeki düğmeler
tk.Button(root, text="Ders Ekleme", command=open_ders_window).pack(pady=10)
tk.Button(root, text="Öğrenci Listesi Yükleme", command=open_ogrenci_window).pack(pady=10)
tk.Button(root, text="Değerlendirme Kriterleri", command=open_criteria_window).pack(pady=10)
tk.Button(root, text="Tablo 1 İşlemleri", command=open_tablo1_window).pack(pady=10)
tk.Button(root, text="Tablo 2 İşlemleri", command=open_tablo2_window).pack(pady=10)
tk.Button(root, text="Tablo Notlar İşlemleri", command=open_tablo_notlar_window).pack(pady=10)  # Notlar işlemleri düğmesi
tk.Button(root, text="Tablo 4 Oluştur", command=generate_tablo4).pack(pady=20)
tk.Button(root, text="Tablo 5 Oluştur", command=create_tablo5).pack(pady=10)
tk.Button(root, text="Çıkış", command=root.quit).pack(pady=10)

# Tabloları oluştur
create_tables()

# Ana döngüyü başlat
root.mainloop()
