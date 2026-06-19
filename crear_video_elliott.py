"""
Generador de Video de Curso - Ondas de Elliott
Convierte cada página del PDF en una escena de video con audio TTS.
Formato final: 1920x1080 (YouTube)

Dependencias:
    pip install pymupdf pillow moviepy gtts pydub
    pip install --upgrade moviepy
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy.editor import (
    ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
)
import tempfile
import shutil

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
PDF_PATH    = r"d:\Descargas\Gian-Victor-Cuevas\ONDAS-DE-ELLIOTT-REGLAS-Y-LEMAS.pdf"
OUTPUT_DIR  = r"d:\Descargas\Gian-Victor-Cuevas\video_output"
OUTPUT_FILE = r"d:\Descargas\Gian-Victor-Cuevas\ondas_de_elliott_curso.mp4"

VIDEO_W, VIDEO_H = 1920, 1080   # YouTube HD
BG_COLOR        = (15, 20, 40)  # Fondo azul oscuro
LANG            = "es"           # Idioma TTS
TTS_SPEED       = False          # False = velocidad normal
DPI             = 180            # Resolución de extracción del PDF
PADDING         = 40             # Margen alrededor de la imagen del PDF
FONT_SIZE_SUB   = 28             # Tamaño de subtítulo en pantalla


# ─── TEXTOS POR PÁGINA (extraídos del PDF) ───────────────────────────────────
# Cada entrada es el texto que se leerá en esa página (índice 0 = página 1)
PAGE_TEXTS = {
    0: "Bienvenidos al curso de Ondas de Elliott. Reglas y Lemas. Volumen uno.",

    1: ("Tabla de contenido. Este curso cubre: Introducción al trading de ondas. "
        "Ondas motrices: Impulsos y Diagonales. "
        "Ondas correctivas: ZigZag, Plana, Triángulos y Combinaciones."),

    2: ("Introducción al trading de ondas. "
        "Solo hay un periódico que dice toda la verdad de un activo: la gráfica de precios. "
        "Charles Dow encontró los patrones repetitivos del mercado. "
        "Ralph Nelson Elliott los estudió con mayor exactitud usando los índices Dow Jones. "
        "La teoría de ondas usa composición fractal y coeficientes de Fibonacci como sustento matemático. "
        "Los tres pilares son: Patrón, Coeficiente y Tiempo. "
        "Los patrones se dividen en motrices y correctivas."),

    3: ("Impulsos. Reglas. "
        "Regla uno: Un impulso siempre se divide en cinco subondas, numeradas del uno al cinco. "
        "Regla dos: La onda dos nunca avanza más allá del inicio de la onda uno."),

    4: ("Impulsos. Reglas continuación. "
        "Regla tres: La onda tres siempre avanza más allá del final de la onda uno. "
        "Regla cuatro: La onda tres nunca es la onda más corta."),

    5: ("Impulsos. Reglas continuación. "
        "Regla cinco: El final de la onda cuatro nunca se encuentra dentro del rango de precios de la onda uno. "
        "Regla seis: La onda tres siempre será de impulso."),

    6: ("Impulsos. Reglas continuación. "
        "Regla siete: Las ondas uno y cinco siempre son motrices. La mayoría de veces, la onda uno es impulso."),

    7: ("Impulsos. Reglas continuación. "
        "Regla ocho: Las ondas dos y cuatro siempre son correctivas. "
        "La onda dos nunca puede ser triángulo."),

    8: ("Impulsos. Lemas. "
        "Lema uno: Las ondas dos y cuatro casi siempre serán patrones distintos. "
        "Lema dos: Algunas veces, la onda cinco no logra superar el final de la onda tres. "
        "Esto se llama fallo de onda cinco, onda cinco fallida, o onda cinco truncada."),

    9: ("Impulsos. Lemas continuación. "
        "Lema tres: La onda dos suele ser ZigZag o combinación de ZigZag. "
        "Lema cuatro: La onda cuatro suele ser plana, triángulo o combinación de planas."),

    10: ("Impulsos. Lemas continuación. "
         "Lema cinco: Dentro de la onda tres casi siempre se encuentra la parte más inclinada del impulso. "
         "La excepción son los llamados Kick Off, donde la onda uno tiene la mayor inclinación."),

    11: ("Impulsos. Lemas continuación. "
         "Lema seis: La onda cinco a menudo termina cuando alcanza o excede ligeramente "
         "una línea paralela a la que conecta los extremos de las ondas dos y cuatro. "
         "Lema siete: Usualmente una de las ondas uno, tres o cinco se extiende."),

    12: ("Impulsos. Lemas continuación. "
         "Lema ocho: La onda extendida de la onda extendida suele ser el mismo número que la onda correspondiente. "
         "Lema nueve: Raramente se extienden dos ondas; cuando ocurre suele ser en temporalidades grandes con las ondas tres y cinco."),

    13: ("Impulsos. Lemas continuación. "
         "Lema diez: La onda uno es la menos común en extenderse. "
         "Lema once: Cuando la onda tres es la extendida, las longitudes de las ondas uno y cinco "
         "suelen ser iguales o estar en relación Fibonacci."),

    14: ("Impulsos. Lemas continuación. "
         "Lema doce: Cuando la onda cinco es extendida, está usualmente en relación Fibonacci "
         "con el recorrido neto desde el inicio de la onda uno hasta el final de la onda tres. "
         "Lema trece: Es típico que la onda cuatro termine en el rango de precios de la onda cuatro de la onda tres."),

    15: ("Impulsos. Lemas continuación. "
         "Lema catorce: La onda cuatro suele dividir todo el impulso en relación de Fibonacci de tiempo y precio."),

    16: ("Diagonales. Reglas. "
         "Regla uno: Comparte las primeras cuatro reglas de los impulsos: "
         "formada por cinco ondas, la onda dos no supera el inicio de la uno, "
         "la onda tres supera el final de la uno, y la onda tres nunca es la más pequeña."),

    17: ("Diagonales. Reglas continuación. "
         "Regla dos: La onda cuatro siempre termina dentro del rango de precios de la onda uno. "
         "Se encontró una única excepción en el Dow Jones de mil novecientos setenta y ocho."),

    18: ("Diagonales. Reglas continuación. "
         "Regla tres: Una diagonal puede ser contráctil o expansiva. "
         "En las contráctiles, cada onda es menor que la anterior. "
         "En las expansivas, cada onda es mayor que la anterior."),

    19: ("Diagonales. Reglas continuación. "
         "Regla cuatro: Las diagonales siempre son la onda inicial o final. "
         "Las diagonales iniciales aparecen como onda uno de un impulso o onda A de un ZigZag. "
         "Las diagonales finales aparecen como onda cinco de un impulso o onda C de un ZigZag o plana."),

    20: ("Diagonales. Reglas continuación. "
         "Regla cinco: En la diagonal inicial, la onda cinco siempre se mueve más allá del final de la onda tres. "
         "En las diagonales finales sí puede existir fallo de onda cinco. "
         "Regla seis: Las ondas de una diagonal final, y las ondas dos y cuatro de las diagonales iniciales, "
         "siempre se subdividen en ZigZags o combinaciones de ZigZags."),

    21: ("Diagonales. Reglas continuación. "
         "Regla siete: Las ondas uno, tres y cinco de las diagonales iniciales "
         "siempre son todas impulsos, o todas ZigZags o combinaciones de ZigZags."),

    22: ("Diagonales. Lemas. "
         "Lema uno: Las ondas dos y cuatro usualmente retroceden de sesenta y seis por ciento "
         "a ochenta y uno por ciento de la onda anterior. "
         "Lema dos: Dentro de un impulso, si la onda uno es una diagonal, la onda tres suele ser extendida."),

    23: ("Diagonales. Lemas continuación. "
         "Lema tres: Dentro de un impulso, no es común que la onda cinco sea una diagonal "
         "si la onda tres no es extendida. "
         "Lema cuatro: En las diagonales contráctiles, la onda cinco termina en o ligeramente superando "
         "la línea que une los finales de las ondas uno y tres. Esto se llama Throw Over."),

    24: ("Diagonales. Lemas continuación. "
         "Lema cinco: En las diagonales expandidas, la onda cinco suele terminar ligeramente "
         "antes de tocar la línea que une los finales de las ondas uno y tres."),

    25: ("ZigZag. Reglas. "
         "Regla uno: Un ZigZag siempre se divide en tres ondas. "
         "Regla dos: La onda B nunca se mueve más allá del inicio de la onda A."),

    26: ("ZigZag. Reglas continuación. "
         "Regla tres: La onda A y la onda C siempre serán ambas ondas motrices. "
         "Regla cuatro: La onda B siempre será correctiva."),

    27: ("ZigZag. Lemas. "
         "Lema uno: La onda A casi siempre se divide en impulso, lo mismo con la onda C. "
         "Lema dos: La onda C casi siempre termina más allá del final de la onda A."),

    28: ("ZigZag. Lemas continuación. "
         "Lema tres: La onda C es usualmente similar en longitud a la onda A. "
         "Lema cuatro: La onda B suele retroceder de treinta y ocho por ciento "
         "a setenta y nueve por ciento de la onda A."),

    29: ("ZigZag. Lemas continuación. "
         "Lema cinco: Si la onda B es un triángulo corrido, suele retroceder de diez a cuarenta por ciento de A. "
         "Lema seis: Si la onda B es un triángulo, suele retroceder de treinta y ocho a cincuenta por ciento de A."),

    30: ("ZigZag. Lemas continuación. "
         "Lema siete: Cuando la onda B es un ZigZag, suele retroceder de cincuenta a setenta y nueve por ciento de la onda A."),

    31: ("ZigZag. Lemas continuación. "
         "Lema ocho: La línea conectando los finales de las ondas A y C es usualmente paralela "
         "a la línea que conecta sus inicios. "
         "La onda C suele terminar una vez alcanza el final de esa línea paralela."),

    32: ("Plana. Reglas. "
         "Regla uno: Una plana siempre se divide en tres ondas. "
         "Regla dos: La onda C siempre es motriz; las ondas A y B siempre son correctivas."),

    33: ("Plana. Reglas continuación. "
         "Regla tres: La onda A nunca es un triángulo. "
         "Regla cuatro: La onda B retrocede al menos a noventa por ciento de la onda A."),

    34: ("Plana. Lemas. "
         "Lema uno: La onda B usualmente retrocede de cien a ciento treinta y ocho por ciento de la onda A. "
         "Lema dos: La onda C es usualmente entre cien y ciento sesenta y cinco por ciento de la onda A."),

    35: ("Plana. Lemas continuación. "
         "Lema tres: La onda C usualmente termina más allá del final de la onda A."),

    36: ("Plana. Notas. "
         "Nota uno: Cuando la onda B retrocede más de ciento cinco por ciento de A "
         "y la onda C termina más allá del final de A, se llama plana extendida. "
         "Nota dos: Cuando la onda B retrocede más de cien por ciento de A "
         "pero la onda C no termina más allá del final de A, se llama plana corrida."),

    37: ("Triángulo Contráctil. Reglas. "
         "El triángulo contráctil se divide en cinco ondas: A, B, C, D y E. "
         "La onda C nunca se mueve más allá del final de la onda A. "
         "La onda D nunca se mueve más allá del final de la onda B. "
         "La onda E nunca se mueve más allá del final de la onda C. "
         "Las líneas que unen los finales de A con C, y B con D, convergen."),

    38: ("Triángulo Contráctil. Reglas continuación. "
         "Regla dos: Al menos cuatro de sus ondas se subdividen en ZigZags simples. "
         "Regla tres: Un triángulo nunca tiene más de una onda que no sea ZigZag. "
         "Esa onda distinta solo puede ser combinación de ZigZags o triángulo."),

    39: ("Triángulo Contráctil. Lemas. "
         "Lema uno: La onda C usualmente se subdivide en combinación de ZigZag, "
         "que dura más y contiene correcciones más profundas que las otras ondas."),

    40: ("Triángulo Contráctil. Lemas continuación. "
         "Lema dos: La onda D a veces se subdivide en combinación de ZigZag con correcciones más profundas. "
         "Lema tres: A veces, una de las ondas, usualmente C, D o E, "
         "se subdivide en un triángulo contráctil o barrido."),

    41: ("Triángulo Contráctil. Lemas continuación. "
         "Lema cuatro: Un sesenta por ciento de las veces, la onda B no supera el inicio de la onda A. "
         "Cuando lo hace, se llama triángulo corrido."),

    42: ("Triángulo Barrido. Reglas. "
         "Sus reglas son muy similares a las del triángulo contráctil: "
         "La onda C nunca se mueve más allá del final de la onda A. "
         "La onda D y B terminan exactamente en el mismo precio. "
         "La onda E nunca se mueve más allá del final de la onda C."),

    43: ("Triángulo Expansivo. Reglas. "
         "Sus reglas son lo contrario al triángulo contráctil: "
         "El final de la onda B siempre supera el inicio de la onda A. "
         "La onda C siempre se mueve más allá del final de la onda A. "
         "La onda D siempre se mueve más allá del final de la onda B. "
         "La onda E siempre se mueve más allá del final de la onda C."),

    44: ("Triángulo Expansivo. Reglas continuación. "
         "Regla dos: Cada una de las ondas B, C y D retroceden al menos cien por ciento "
         "pero no más de ciento cincuenta por ciento de la onda anterior."),

    45: ("Triángulo Expansivo. Lemas. "
         "Lema uno: Las ondas B, C y D usualmente retroceden de ciento cinco a ciento veinticinco por ciento. "
         "Lema dos: Hasta el momento no se ha visto que alguna onda de un triángulo expansivo "
         "se subdivida en un triángulo."),

    46: ("Combinaciones. Reglas. "
         "Las combinaciones o correcciones complejas se forman por dos o tres patrones correctivos simples, "
         "separados por ondas X en dirección opuesta. "
         "Con dos patrones se llaman W e Y. Con tres patrones se llaman W, Y y Z."),

    47: ("Combinaciones. Reglas continuación. "
         "Regla dos: Una combinación de ZigZags se llama doble ZigZag si son dos, "
         "y triple ZigZag si son tres."),

    48: ("Combinaciones. Reglas continuación. "
         "Regla tres: A excepción del doble ZigZag, las demás combinaciones de dos patrones "
         "se llaman doble tres, y pueden ser: ZigZag y plana, plana y ZigZag, "
         "plana y plana, ZigZag y triángulo, o plana y triángulo."),

    49: ("Combinaciones. Reglas continuación. "
         "Regla cuatro: Un raro triple tres comprende tres planas. "
         "Regla cinco: Nunca se ha visto que un triángulo expansivo sea parte de una combinación."),

    50: ("Combinaciones. Reglas continuación. "
         "Regla seis: Dobles y triples ZigZags toman el sitio del ZigZag. "
         "Dobles y triples tres toman el lugar de las planas y triángulos."),

    51: ("Combinaciones. Lemas. "
         "Cuando un ZigZag o una plana se presentan como parte de una combinación, "
         "se identifican dentro del contexto de ondas W, X e Y."),

    52: ("Epílogo. "
         "El objetivo de mostrar todas las reglas es reducir la subjetividad "
         "y evitar conteos o análisis erróneos. "
         "Lo siguiente es aplicar estas reglas mediante la práctica. "
         "Como analista proyectas lo que es más probable que suceda. "
         "Como trader debes dominar la gestión de riesgo, el seguimiento de operaciones, "
         "ajustar stop loss y tomar decisiones para proteger el capital. "
         "El mundo del trading es amplio y es importante seguir aprendiendo."),
}


# ─── FUNCIONES ────────────────────────────────────────────────────────────────

def setup_dirs():
    """Crea los directorios de trabajo."""
    dirs = [
        OUTPUT_DIR,
        os.path.join(OUTPUT_DIR, "pages"),
        os.path.join(OUTPUT_DIR, "audio"),
        os.path.join(OUTPUT_DIR, "frames"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print(f"[✓] Directorios creados en: {OUTPUT_DIR}")


def extract_pdf_pages(pdf_path: str) -> list[str]:
    """Extrae cada página del PDF como imagen PNG."""
    pages_dir = os.path.join(OUTPUT_DIR, "pages")
    doc = fitz.open(pdf_path)
    saved = []
    print(f"[→] Extrayendo {len(doc)} páginas del PDF...")
    for i, page in enumerate(doc):
        mat = fitz.Matrix(DPI / 72, DPI / 72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        out = os.path.join(pages_dir, f"page_{i:03d}.png")
        pix.save(out)
        saved.append(out)
        print(f"    Página {i+1}/{len(doc)} extraída", end="\r")
    print(f"\n[✓] {len(saved)} páginas extraídas.")
    doc.close()
    return saved


def build_frame(page_img_path: str, page_num: int, total: int) -> str:
    """
    Compone un frame 1920x1080 con:
    - Fondo oscuro
    - Imagen del PDF centrada y escalada
    - Barra inferior con número de página
    """
    frames_dir = os.path.join(OUTPUT_DIR, "frames")
    out_path = os.path.join(frames_dir, f"frame_{page_num:03d}.png")

    canvas = Image.new("RGB", (VIDEO_W, VIDEO_H), BG_COLOR)
    pdf_img = Image.open(page_img_path).convert("RGB")

    # Área disponible para la imagen (con padding)
    avail_w = VIDEO_W - PADDING * 2
    avail_h = VIDEO_H - PADDING * 2 - 60  # 60px para barra inferior

    # Escalar manteniendo proporción
    ratio = min(avail_w / pdf_img.width, avail_h / pdf_img.height)
    new_w = int(pdf_img.width * ratio)
    new_h = int(pdf_img.height * ratio)
    pdf_img = pdf_img.resize((new_w, new_h), Image.LANCZOS)

    # Centrar
    x = (VIDEO_W - new_w) // 2
    y = (VIDEO_H - 60 - new_h) // 2
    canvas.paste(pdf_img, (x, y))

    # Barra inferior
    draw = ImageDraw.Draw(canvas)
    bar_y = VIDEO_H - 55
    draw.rectangle([0, bar_y, VIDEO_W, VIDEO_H], fill=(10, 14, 30))

    # Línea separadora
    draw.rectangle([0, bar_y, VIDEO_W, bar_y + 2], fill=(50, 100, 200))

    # Texto de página
    label = f"Ondas de Elliott — Reglas y Lemas  |  Página {page_num + 1} de {total}"
    try:
        font = ImageFont.truetype("arial.ttf", FONT_SIZE_SUB)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), label, font=font)
    tw = bbox[2] - bbox[0]
    tx = (VIDEO_W - tw) // 2
    ty = bar_y + 12
    draw.text((tx, ty), label, fill=(180, 200, 255), font=font)

    canvas.save(out_path, "PNG")
    return out_path


def generate_audio(text: str, page_num: int) -> str:
    """Genera audio TTS para el texto de una página."""
    audio_dir = os.path.join(OUTPUT_DIR, "audio")
    out_path = os.path.join(audio_dir, f"audio_{page_num:03d}.mp3")

    if os.path.exists(out_path):
        print(f"    Audio página {page_num+1} ya existe, omitiendo.")
        return out_path

    tts = gTTS(text=text, lang=LANG, slow=TTS_SPEED)
    tts.save(out_path)
    return out_path


def get_audio_duration(audio_path: str) -> float:
    """Retorna la duración en segundos de un archivo de audio."""
    clip = AudioFileClip(audio_path)
    dur = clip.duration
    clip.close()
    return dur


def make_page_clip(frame_path: str, audio_path: str) -> object:
    """
    Crea un VideoClip para una página:
    - Imagen estática con duración = duración del audio + 0.5s de pausa
    """
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration + 0.8  # pequeña pausa al final

    video_clip = (
        ImageClip(frame_path)
        .set_duration(duration)
        .set_audio(audio_clip)
    )
    return video_clip


def build_intro_frame() -> str:
    """Crea el frame de portada del curso."""
    frames_dir = os.path.join(OUTPUT_DIR, "frames")
    out_path = os.path.join(frames_dir, "frame_intro.png")

    canvas = Image.new("RGB", (VIDEO_W, VIDEO_H), (10, 14, 30))
    draw = ImageDraw.Draw(canvas)

    # Gradiente simple con rectángulos
    for i in range(VIDEO_H // 2):
        alpha = i / (VIDEO_H // 2)
        r = int(10 + 20 * alpha)
        g = int(14 + 30 * alpha)
        b = int(30 + 60 * alpha)
        draw.rectangle([0, i, VIDEO_W, i + 1], fill=(r, g, b))

    try:
        font_big   = ImageFont.truetype("arialbd.ttf", 90)
        font_med   = ImageFont.truetype("arial.ttf",   48)
        font_small = ImageFont.truetype("arial.ttf",   32)
    except Exception:
        font_big   = ImageFont.load_default()
        font_med   = font_big
        font_small = font_big

    # Línea decorativa superior
    draw.rectangle([160, 200, VIDEO_W - 160, 206], fill=(50, 120, 255))

    # Título principal
    title1 = "ONDAS DE ELLIOTT"
    bb = draw.textbbox((0, 0), title1, font=font_big)
    draw.text(((VIDEO_W - (bb[2]-bb[0])) // 2, 240), title1,
              fill=(255, 255, 255), font=font_big)

    # Subtítulo
    title2 = "REGLAS Y LEMAS"
    bb2 = draw.textbbox((0, 0), title2, font=font_med)
    draw.text(((VIDEO_W - (bb2[2]-bb2[0])) // 2, 380), title2,
              fill=(100, 160, 255), font=font_med)

    # Vol
    vol = "VOL. 1 — CURSO COMPLETO"
    bb3 = draw.textbbox((0, 0), vol, font=font_small)
    draw.text(((VIDEO_W - (bb3[2]-bb3[0])) // 2, 470), vol,
              fill=(150, 180, 220), font=font_small)

    # Línea decorativa inferior
    draw.rectangle([160, 540, VIDEO_W - 160, 546], fill=(50, 120, 255))

    # Descripción
    desc = "Impulsos · Diagonales · ZigZag · Plana · Triángulos · Combinaciones"
    bb4 = draw.textbbox((0, 0), desc, font=font_small)
    draw.text(((VIDEO_W - (bb4[2]-bb4[0])) // 2, 600), desc,
              fill=(120, 150, 200), font=font_small)

    canvas.save(out_path, "PNG")
    return out_path


# ─── PROGRAMA PRINCIPAL ───────────────────────────────────────────────────────

def main():
    print("\n" + "="*60)
    print("  GENERADOR DE CURSO — ONDAS DE ELLIOTT")
    print("="*60 + "\n")

    # 1. Directorios
    setup_dirs()

    # 2. Extraer páginas del PDF
    page_images = extract_pdf_pages(PDF_PATH)
    total_pages = len(page_images)

    # 3. Generar frame de portada + audio de portada
    print("\n[→] Creando portada del curso...")
    intro_frame = build_intro_frame()
    intro_text  = ("Bienvenidos al curso de Ondas de Elliott, Reglas y Lemas, Volumen uno. "
                   "En este curso aprenderás todas las reglas y lemas que conforman "
                   "la teoría de ondas de Elliott, desde los impulsos hasta las combinaciones.")
    intro_audio = generate_audio(intro_text, page_num=-1)
    # guardarlo con nombre especial
    intro_audio_path = os.path.join(OUTPUT_DIR, "audio", "audio_intro.mp3")
    if not os.path.exists(intro_audio_path):
        tts_intro = __import__("gtts").gTTS(text=intro_text, lang=LANG, slow=TTS_SPEED)
        tts_intro.save(intro_audio_path)
    print("[✓] Portada creada.")

    # 4. Construir frames + audio para cada página
    clips = []

    # Clip de portada
    intro_clip = make_page_clip(intro_frame, intro_audio_path)
    clips.append(intro_clip)
    print("[✓] Clip de portada listo.")

    # Clips por página
    print(f"\n[→] Procesando {total_pages} páginas...")
    for i, page_img in enumerate(page_images):

        # Frame 1920x1080
        frame_path = build_frame(page_img, i, total_pages)

        # Texto para TTS
        text = PAGE_TEXTS.get(i, f"Página {i + 1}.")

        # Audio
        audio_path = os.path.join(OUTPUT_DIR, "audio", f"audio_{i:03d}.mp3")
        if not os.path.exists(audio_path):
            print(f"  [TTS] Generando audio página {i+1}/{total_pages}...")
            tts = __import__("gtts").gTTS(text=text, lang=LANG, slow=TTS_SPEED)
            tts.save(audio_path)
        else:
            print(f"  [TTS] Audio página {i+1} ya existe.")

        # Clip
        clip = make_page_clip(frame_path, audio_path)
        clips.append(clip)
        print(f"  [✓] Clip {i+1}/{total_pages} listo  "
              f"(duración: {clip.duration:.1f}s)")

    # 5. Concatenar todos los clips
    print(f"\n[→] Concatenando {len(clips)} clips...")
    final = concatenate_videoclips(clips, method="compose")

    total_dur = sum(c.duration for c in clips)
    mins = int(total_dur // 60)
    secs = int(total_dur % 60)
    print(f"[✓] Duración total del video: {mins}m {secs}s")

    # 6. Exportar video final
    print(f"\n[→] Exportando video final a:\n    {OUTPUT_FILE}")
    print("    (Esto puede tardar varios minutos...)\n")

    final.write_videofile(
        OUTPUT_FILE,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        preset="medium",       # balance velocidad/calidad
        bitrate="4000k",       # buena calidad para YouTube
        audio_bitrate="192k",
        threads=4,
        logger="bar",
    )

    # 7. Cerrar clips para liberar memoria
    for c in clips:
        c.close()
    final.close()

    print("\n" + "="*60)
    print(f"  ✅ VIDEO GENERADO EXITOSAMENTE")
    print(f"  📁 {OUTPUT_FILE}")
    print(f"  ⏱  Duración: {mins}m {secs}s")
    print(f"  📐 Resolución: {VIDEO_W}x{VIDEO_H} (YouTube HD)")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
