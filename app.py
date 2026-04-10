import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image

# Importando a classe do outro arquivo!
from image_processer import ImageProcesser

# Configurações globais do CustomTkinter
ctk.set_appearance_mode("Dark")  # Modos: "System" (padrão), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Temas: "blue" (padrão), "green", "dark-blue"

class App:
    def __init__(self, image_processer, image_path):
        self.processor = image_processer
        self.image_path = image_path
        
        # Carrega a imagem original
        self.original_cv_img = cv2.imread(self.image_path)
        if self.original_cv_img is None:
            # Cria uma imagem preta de placeholder se o arquivo não for encontrado
            print(f"Aviso: Imagem '{self.image_path}' não encontrada. Usando fundo preto.")
            self.original_cv_img = np.zeros((300, 400, 3), dtype=np.uint8)
            
        self.original_cv_img = cv2.resize(self.original_cv_img, (400, 300))

        # Cria um buffer vazio (uma tela de pintura) com o exato mesmo tamanho e tipo
        self.img_buffer = np.empty_like(self.original_cv_img)

        # Configuração da janela principal
        self.root = ctk.CTk()
        self.root.title("Calibrador HSV e Kernel")
        self.root.geometry("900x600")
        
        self.window()
        self.config()
        self.atualizar_imagens()

    def window(self):
        """Configura o layout principal da janela."""
        self.frame_imagens = ctk.CTkFrame(self.root, fg_color="transparent")
        self.frame_imagens.pack(pady=20)

        # Usamos Textos em cima e CTkLabels vazios embaixo para receber as imagens
        ctk.CTkLabel(self.frame_imagens, text="Original", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10)
        self.lbl_original = ctk.CTkLabel(self.frame_imagens, text="")
        self.lbl_original.grid(row=1, column=0, padx=10)

        ctk.CTkLabel(self.frame_imagens, text="Processada", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10)
        self.lbl_processada = ctk.CTkLabel(self.frame_imagens, text="")
        self.lbl_processada.grid(row=1, column=1, padx=10)

        self.frame_controles = ctk.CTkFrame(self.root)
        self.frame_controles.pack(pady=10, fill="x", padx=40)

    def validar_digitacao(self, event=None):
        """Lê os valores das caixinhas, valida e atualiza os sliders."""
        try:
            # Atualiza sliders Lower
            self.sl_h_min.set(int(self.entry_h_min.get()))
            self.sl_s_min.set(int(self.entry_s_min.get()))
            self.sl_v_min.set(int(self.entry_v_min.get()))
            
            # Atualiza sliders Upper
            self.sl_h_max.set(int(self.entry_h_max.get()))
            self.sl_s_max.set(int(self.entry_s_max.get()))
            self.sl_v_max.set(int(self.entry_v_max.get()))
            
            # Atualiza Kernel (garantindo que seja ímpar)
            k_val = int(self.entry_kernel.get())
            kernel_size = k_val if k_val % 2 != 0 else k_val + 1
            self.sl_kernel.set(kernel_size)
            
            # Força a atualização visual das caixinhas (caso o usuário tenha digitado um kernel par, ele corrige na tela)
            self.atualizar_textos()
            
        except ValueError:
            # Se o usuário digitar letras ou vazio, ignoramos o erro e voltamos os textos aos valores originais dos sliders
            self.atualizar_textos()

    def atualizar_textos(self, event=None):
        """Atualiza as caixinhas de entrada em tempo real conforme o slider se move."""
        # Função auxiliar para não repetir código
        def set_entry(entry, valor):
            entry.delete(0, "end") # Apaga o texto atual
            entry.insert(0, str(int(valor))) # Insere o novo valor

        # Lower HSV
        set_entry(self.entry_h_min, self.sl_h_min.get())
        set_entry(self.entry_s_min, self.sl_s_min.get())
        set_entry(self.entry_v_min, self.sl_v_min.get())
        
        # Upper HSV
        set_entry(self.entry_h_max, self.sl_h_max.get())
        set_entry(self.entry_s_max, self.sl_s_max.get())
        set_entry(self.entry_v_max, self.sl_v_max.get())
        
        # Kernel
        k_val = int(self.sl_kernel.get())
        kernel_size = k_val if k_val % 2 != 0 else k_val + 1
        set_entry(self.entry_kernel, kernel_size)

    def config(self):
        """Configura os sliders, caixas de entrada e o botão."""
        # --- Lower HSV ---
        ctk.CTkLabel(self.frame_controles, text="Lower HSV (H, S, V)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=3, pady=5)
        
        self.sl_h_min = ctk.CTkSlider(self.frame_controles, from_=0, to=179, width=150, command=self.atualizar_textos)
        self.sl_s_min = ctk.CTkSlider(self.frame_controles, from_=0, to=255, width=150, command=self.atualizar_textos)
        self.sl_v_min = ctk.CTkSlider(self.frame_controles, from_=0, to=255, width=150, command=self.atualizar_textos)
        
        self.sl_h_min.grid(row=1, column=0, padx=10)
        self.sl_s_min.grid(row=1, column=1, padx=10)
        self.sl_v_min.grid(row=1, column=2, padx=10)

        # ENTRIES (Caixinhas de texto) - Lower
        self.entry_h_min = ctk.CTkEntry(self.frame_controles, width=50, justify="center")
        self.entry_s_min = ctk.CTkEntry(self.frame_controles, width=50, justify="center")
        self.entry_v_min = ctk.CTkEntry(self.frame_controles, width=50, justify="center")
        
        self.entry_h_min.grid(row=2, column=0, pady=(0, 10))
        self.entry_s_min.grid(row=2, column=1, pady=(0, 10))
        self.entry_v_min.grid(row=2, column=2, pady=(0, 10))

        # Configura valores iniciais
        self.sl_h_min.set(5)
        self.sl_s_min.set(100)
        self.sl_v_min.set(100)

        # --- Upper HSV ---
        ctk.CTkLabel(self.frame_controles, text="Upper HSV (H, S, V)", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, columnspan=3, pady=(15,5))
        
        self.sl_h_max = ctk.CTkSlider(self.frame_controles, from_=0, to=179, width=150, command=self.atualizar_textos)
        self.sl_s_max = ctk.CTkSlider(self.frame_controles, from_=0, to=255, width=150, command=self.atualizar_textos)
        self.sl_v_max = ctk.CTkSlider(self.frame_controles, from_=0, to=255, width=150, command=self.atualizar_textos)
        
        self.sl_h_max.grid(row=4, column=0, padx=10)
        self.sl_s_max.grid(row=4, column=1, padx=10)
        self.sl_v_max.grid(row=4, column=2, padx=10)

        # ENTRIES (Caixinhas de texto) - Upper
        self.entry_h_max = ctk.CTkEntry(self.frame_controles, width=50, justify="center")
        self.entry_s_max = ctk.CTkEntry(self.frame_controles, width=50, justify="center")
        self.entry_v_max = ctk.CTkEntry(self.frame_controles, width=50, justify="center")
        
        self.entry_h_max.grid(row=5, column=0, pady=(0, 10))
        self.entry_s_max.grid(row=5, column=1, pady=(0, 10))
        self.entry_v_max.grid(row=5, column=2, pady=(0, 10))

        # Configura valores iniciais
        self.sl_h_max.set(15)
        self.sl_s_max.set(255)
        self.sl_v_max.set(255)

        # --- Kernel ---
        ctk.CTkLabel(self.frame_controles, text="Kernel Size", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, pady=5, padx=30)
        self.sl_kernel = ctk.CTkSlider(self.frame_controles, from_=1, to=31, number_of_steps=15, width=150, command=self.atualizar_textos)
        self.sl_kernel.grid(row=1, column=3, padx=30)
        
        self.entry_kernel = ctk.CTkEntry(self.frame_controles, width=50, justify="center")
        self.entry_kernel.grid(row=2, column=3, pady=(0, 10))
        self.sl_kernel.set(5)

        # --- Gatilhos (Binds) para digitação ---
        # Quando o usuário aperta Enter ou clica fora de qualquer caixinha, chama a função validar_digitacao
        entradas = [self.entry_h_min, self.entry_s_min, self.entry_v_min, 
                    self.entry_h_max, self.entry_s_max, self.entry_v_max, self.entry_kernel]
        
        for entrada in entradas:
            entrada.bind("<Return>", self.validar_digitacao)  # Aperta Enter
            entrada.bind("<FocusOut>", self.validar_digitacao) # Clica fora da caixinha

        # --- Botão de Aplicar ---
        self.btn_aplicar = ctk.CTkButton(self.frame_controles, text="Aplicar Filtros", command=self.atualizar_imagens, fg_color="green", hover_color="darkgreen")
        self.btn_aplicar.grid(row=4, column=3, rowspan=2, padx=30, pady=(10,0))
        
        # Chama uma vez no início para garantir que os textos comecem sincronizados
        self.atualizar_textos()

    def atualizar_imagens(self):
        """Converte os valores e atualiza a interface usando CTkImage."""
        # 1. Coleta e converte os valores para inteiros (CTkslider retorna float)
        lower_hsv = np.array([int(self.sl_h_min.get()), int(self.sl_s_min.get()), int(self.sl_v_min.get())])
        upper_hsv = np.array([int(self.sl_h_max.get()), int(self.sl_s_max.get()), int(self.sl_v_max.get())])
        
        # Garante que o kernel seja sempre um número ímpar
        k_val = int(self.sl_kernel.get())
        kernel_size = k_val if k_val % 2 != 0 else k_val + 1

        # 2. Processa a imagem usando a classe importada
        img_linha, img_processada = self.processor.pipeline(
            self.original_cv_img, 
            self.img_buffer, 
            lower_hsv, 
            upper_hsv, 
            kernel_size
            )

        # 3. Conversão para o formato moderno do CustomTkinter (CTkImage)
        # Original
        img_rgb_orig = cv2.cvtColor(img_linha, cv2.COLOR_BGR2RGB)
        img_pil_orig = Image.fromarray(img_rgb_orig)
        img_ctk_orig = ctk.CTkImage(light_image=img_pil_orig, dark_image=img_pil_orig, size=(400, 300))

        # Processada
        if len(img_processada.shape) == 2:
            img_rgb_proc = cv2.cvtColor(img_processada, cv2.COLOR_GRAY2RGB)
        else:
            img_rgb_proc = cv2.cvtColor(img_processada, cv2.COLOR_BGR2RGB)
            
        img_pil_proc = Image.fromarray(img_rgb_proc)
        img_ctk_proc = ctk.CTkImage(light_image=img_pil_proc, dark_image=img_pil_proc, size=(400, 300))

        # 4. Atualiza os Labels
        self.lbl_original.configure(image=img_ctk_orig)
        self.lbl_processada.configure(image=img_ctk_proc)

    def app(self):
        """Inicia o loop."""
        self.root.mainloop()

# ==========================================
if __name__ == "__main__":
    caminho_da_imagem = 'hose.jpg' 
    
    # Instancia a classe do arquivo processador_imagem.py
    processador = ImageProcesser() 
    
    aplicativo = App(processador, caminho_da_imagem)
    aplicativo.app()