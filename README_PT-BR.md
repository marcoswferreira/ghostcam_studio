# GhostCam Studio — Motor de Efeitos Visuais em Tempo Real para Webcam

O **GhostCam Studio** é um motor de efeitos visuais (VFX) em tempo real para webcam construído com MediaPipe e OpenCV. Todo o processamento acontece 100% localmente no seu computador, gerando uma imagem limpa (sem textos ou menus sobrepostos no vídeo) tanto na janela de pré-visualização quanto na Câmera Virtual (Microsoft Teams, Google Meet, Zoom, Discord e OBS Studio).

> 🇺🇸 Read this documentation in English: [README.md](README.md)

---

## ✨ 5 Efeitos Visuais Inclusos

Você pode escolher o efeito no menu inicial **ou trocar de efeito ao vivo a qualquer momento** apertando as teclas **`1` a `5`** com a janela da câmera aberta:

| Tecla | Modo | Gesto com as Mãos | Efeito Visual e Sonoro |
| :---: | :--- | :--- | :--- |
| **`1`** | **Instant Teleport** (Teletransporte) | Encoste **indicador + médio juntos na testa** por 1,0s | Linhas de velocidade estilo anime comprimem sua silhueta com o som clássico de teletransporte; repita o gesto para reaparecer com o efeito reverso. |
| **`2`** | **Cosmic Disintegration** (Desintegração) | Sinal de **"V" (paz e amor)** | Sua silhueta se desfaz em fragmentos e fagulhas luminosas levadas pelo vento em 2,15 segundos. |
| **`3`** | **Ninja Smoke Bomb** (Bomba de Fumaça) | **Junte as duas palmas abertas** na frente do peito | Uma nuvem densa de fumaça explode ao seu redor e um pergaminho ninja cai no seu lugar com física de impacto. |
| **`4`** | **Optical Stealth Cloak** (Camuflagem Predador) | Levante uma **mão aberta (5 dedos)** | Camuflagem óptica estilo Predador/Cyberpunk que refrata o fundo através da sua silhueta com borda holográfica neon. Even invisível, se você se mexer, uma leve distorção de lente acompanha seu movimento! |
| **`5`** | **Dimensional Portal** (Portal Dimensional) | Gesto de **Rock / Chifres** (indicador + mindinho levantados) | Um vórtice de energia giratório se abre atrás de você, suga sua silhueta em espiral para o centro do portal e se fecha. |

Todos os 5 efeitos contam com efeitos sonoros estéreo sintetizados proceduralmente pelo módulo `ghostcam/audio.py`.

---

## 🚀 Como Começar

1. Dê um duplo clique em **`start_studio.bat`**.
2. Escolha o efeito inicial (`1` a `5`) na janela **GhostCam Studio**.
3. **Saia da frente da câmera por 4 segundos** enquanto o fundo vazio é capturado.
4. Volte para a frente da câmera e faça o gesto do efeito (ou aperte **`V`**)!

### Iniciar diretamente em um modo pelo terminal:
```powershell
.\start_studio.bat --mode teleport
.\start_studio.bat --mode disintegration
.\start_studio.bat --mode smoke
.\start_studio.bat --mode stealth
.\start_studio.bat --mode portal
```

---

## 🎥 Como usar no Microsoft Teams, Meet, Zoom, Discord e OBS

1. Instale o [OBS Studio](https://obsproject.com/) (que instala o driver **OBS Virtual Camera** no Windows):
   ```powershell
   winget install OBSProject.OBSStudio
   ```
2. Abra primeiro o **`start_studio.bat`** (ou **`start_virtual_cam.bat`**) com o OBS fechado.
3. No Microsoft Teams / Meet / Zoom / Discord, vá nas configurações de vídeo e selecione **`OBS Virtual Camera`**.

---

## ⌨️ Atalhos de Teclado (na janela da câmera ao vivo)

- **`1` a `5`**: Troca entre os 5 efeitos instantaneamente sem precisar fechar o programa.
- **`ESPAÇO`**: Captura um novo fundo vazio (saia da câmera por 4 segundos).
- **`V`**: Dispara manualmente o efeito de desaparecimento atual.
- **`R`**: Faz você reaparecer na câmera (com animação reversa nos modos Teletransporte, Camuflagem e Portal).
- **`F`**: Alterna tela cheia (fullscreen).
- **`Q` ou `ESC`**: Fecha o programa.
