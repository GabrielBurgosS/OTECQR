"""
QR Generator - Impronta
Genera QR codes con logo opcional a partir de una URL.
Empaquetable como .exe portable con PyInstaller.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import qrcode
import io

# ── Portapapeles: win32clipboard es la única forma confiable en Windows ───────
try:
    import win32clipboard
    import win32con
    _WIN32_AVAILABLE = True
except ImportError:
    _WIN32_AVAILABLE = False


def copy_image_to_clipboard(img: Image.Image) -> bool:
    """
    Copia un PIL Image al portapapeles de Windows como bitmap.
    Retorna True si tuvo éxito, False si win32clipboard no está disponible.
    """
    if not _WIN32_AVAILABLE:
        return False

    # Convertir a BMP en memoria (formato que acepta el portapapeles de Windows)
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="BMP")
    bmp_data = buf.getvalue()

    # El portapapeles espera BMP sin los primeros 14 bytes del file header
    dib_data = bmp_data[14:]

    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_DIB, dib_data)
    finally:
        win32clipboard.CloseClipboard()

    return True


# ── Utilidad para rutas (compatibilidad con PyInstaller) ──────────────────────
def resource_path(relative_path):
    """Resuelve rutas tanto en modo script como en .exe empaquetado."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# ── Generación del QR ─────────────────────────────────────────────────────────
def generate_qr(url: str, logo_path: str = None,
                fill_color: str = "#007A5E", back_color: str = "white",
                box_size: int = 10, border: int = 4) -> Image.Image:
    """
    Genera un QR code con colores personalizados y logo opcional.
    Retorna un objeto PIL Image.
    """
    if not url.strip():
        raise ValueError("La URL no puede estar vacía.")

    ec = qrcode.constants.ERROR_CORRECT_H if logo_path else qrcode.constants.ERROR_CORRECT_M
    qr = qrcode.QRCode(
        version=5,
        error_correction=ec,
        box_size=box_size,
        border=border,
    )
    qr.add_data(url.strip())
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")

    # ── Insertar logo centrado si se entrega uno ────────────────────────────── 
    if logo_path and os.path.isfile(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        qr_w, qr_h = qr_img.size
        max_logo = qr_w // 4          # logo ocupa máx. 25 % del ancho del QR
        logo.thumbnail((max_logo, max_logo), Image.LANCZOS)

        logo_w, logo_h = logo.size
        pos = ((qr_w - logo_w) // 2, (qr_h - logo_h) // 2)

        # Fondo blanco detrás del logo para no romper lectura
        padding = 6
        bg = Image.new("RGBA", (logo_w + padding * 2, logo_h + padding * 2), "white")
        bg_pos = (pos[0] - padding, pos[1] - padding)
        qr_img.paste(bg, bg_pos)
        qr_img.paste(logo, pos, mask=logo)

    return qr_img.convert("RGB")


# ── Ventana principal ─────────────────────────────────────────────────────────
class QRApp(tk.Tk):
    FILL_DEFAULT  = "#007A5E"
    BACK_DEFAULT  = "#FFFFFF"
    PREVIEW_SIZE  = 300

    def __init__(self):
        super().__init__()
        self.title("QR Generator – Impronta")
        self.resizable(False, False)
        self._qr_image    = None          # PIL Image resultante
        self._preview_img = None          # ImageTk (evita GC)
        self._build_ui()
        self._center_window()

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        pad = dict(padx=10, pady=6)

        # ── Encabezado ────────────────────────────────────────────────────────
        header = tk.Frame(self, bg=self.FILL_DEFAULT)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        tk.Label(header, text="  QR Generator", bg=self.FILL_DEFAULT,
                 fg="white", font=("Segoe UI", 14, "bold"),
                 anchor="w", pady=10).pack(fill="x")

        # ── URL ───────────────────────────────────────────────────────────────
        tk.Label(self, text="URL o texto a codificar:",
                 font=("Segoe UI", 9, "bold")).grid(
                 row=1, column=0, columnspan=2, sticky="w", **pad)
        self._url_var = tk.StringVar()
        url_entry = ttk.Entry(self, textvariable=self._url_var, width=52,
                              font=("Segoe UI", 10))
        url_entry.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=2)
        url_entry.bind("<Return>", lambda _: self._on_generate())

        # ── Botón generar ─────────────────────────────────────────────────────
        self._gen_btn = ttk.Button(self, text="⚡  Generar QR",
                                   command=self._on_generate)
        self._gen_btn.grid(row=6, column=0, columnspan=2,
                           pady=(2, 8), padx=10, sticky="ew")

        # ── Preview ───────────────────────────────────────────────────────────
        self._preview_canvas = tk.Canvas(self, width=self.PREVIEW_SIZE,
                                         height=self.PREVIEW_SIZE, bg="#f0f0f0",
                                         highlightthickness=1, highlightbackground="#cccccc")
        self._preview_canvas.grid(row=7, column=0, columnspan=2, padx=10, pady=4)
        self._placeholder_text = self._preview_canvas.create_text(
            self.PREVIEW_SIZE // 2, self.PREVIEW_SIZE // 2,
            text="El QR aparecerá aquí", fill="#aaaaaa",
            font=("Segoe UI", 10, "italic"))

        # ── Botones: Copiar y Guardar ─────────────────────────────────────────
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=8, column=0, columnspan=2,
                       pady=(4, 4), padx=10, sticky="ew")
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        self._copy_btn = ttk.Button(btn_frame, text="📋  Copiar imagen",
                                    command=self._on_copy, state="disabled")
        self._copy_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self._save_btn = ttk.Button(btn_frame, text="💾  Guardar imagen…",
                                    command=self._on_save, state="disabled")
        self._save_btn.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        # ── Menú contextual (clic derecho sobre el preview) ───────────────────
        self._ctx_menu = tk.Menu(self, tearoff=0)
        self._ctx_menu.add_command(label="📋  Copiar imagen",
                                   command=self._on_copy)
        self._ctx_menu.add_separator()
        self._ctx_menu.add_command(label="💾  Guardar imagen…",
                                   command=self._on_save)
        self._preview_canvas.bind("<Button-3>", self._show_context_menu)

        # ── Status ────────────────────────────────────────────────────────────
        self._status = tk.StringVar(value="Listo.")
        tk.Label(self, textvariable=self._status, fg="gray",
                 font=("Segoe UI", 8), anchor="w").grid(
                 row=9, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 6))

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    # ── Acciones principales ──────────────────────────────────────────────────
    def _on_generate(self):
        url = self._url_var.get()
        if not url.strip():
            messagebox.showwarning("Atención", "Ingresa una URL o texto primero.")
            return
        self._status.set("Generando…")
        self.update_idletasks()
        try:
            self._qr_image = generate_qr(url=url)
            self._show_preview(self._qr_image)
            self._save_btn.config(state="normal")
            self._copy_btn.config(state="normal")
            self._status.set("✅ QR generado. Clic derecho sobre el preview para más opciones.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._status.set(f"Error: {e}")

    def _show_preview(self, img: Image.Image):
        preview = img.copy()
        preview.thumbnail((self.PREVIEW_SIZE, self.PREVIEW_SIZE), Image.LANCZOS)
        self._preview_img = ImageTk.PhotoImage(preview)
        self._preview_canvas.delete("all")
        cx, cy = self.PREVIEW_SIZE // 2, self.PREVIEW_SIZE // 2
        self._preview_canvas.create_image(cx, cy, anchor="center",
                                          image=self._preview_img)

    def _on_copy(self):
        """Copia el QR al portapapeles de Windows como bitmap."""
        if self._qr_image is None:
            return
        if not _WIN32_AVAILABLE:
            messagebox.showwarning(
                "No disponible",
                "La función de copiar requiere el paquete 'pywin32'.\n"
                "Instálalo con: pip install pywin32\n\n"
                "Luego recompila el .exe con PyInstaller.")
            return
        try:
            ok = copy_image_to_clipboard(self._qr_image)
            if ok:
                self._status.set("📋 Imagen copiada al portapapeles.")
        except Exception as e:
            messagebox.showerror("Error al copiar", str(e))

    def _show_context_menu(self, event: tk.Event):
        """Muestra el menú contextual solo si ya hay un QR generado."""
        if self._qr_image is None:
            return
        try:
            self._ctx_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self._ctx_menu.grab_release()

    def _on_save(self):
        if self._qr_image is None:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Todos", "*.*")],
            initialfile="qr_impronta.png",
            title="Guardar QR")
        if path:
            self._qr_image.save(path)
            self._status.set(f"✅ Guardado en {os.path.basename(path)}")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QRApp()
    app.mainloop()
