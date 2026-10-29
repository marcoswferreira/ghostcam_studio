# GhostCam Studio — Motor de Efeitos Visuais em Tempo Real para Webcam

O **GhostCam Studio** é um motor independente de efeitos visuais (VFX) em tempo real para webcam construído com MediaPipe e OpenCV. Todo o processamento de vídeo, sprites e efeitos sonoros estéreo são gerados 100% proceduralmente no seu próprio computador, produzindo uma imagem limpa (sem textos sobrepostos no vídeo) tanto na janela de pré-visualização quanto na Câmera Virtual (Microsoft Teams, Google Meet, Zoom, Discord e OBS Studio).

> 🇺🇸 Read this documentation in English: [README.md](README.md)

---

## ✨ 7 Efeitos Visuais Inclusos

Você pode escolher o efeito no menu inicial **ou trocar de efeito ao vivo a qualquer momento** apertando as teclas **`1` a `7`** com a janela da câmera aberta:

| Tecla | Modo | Gesto com as Mãos | Efeito Visual e Sonoro (100% Procedural) |
| :---: | :--- | :--- | :--- |
| **`1`** | **Normal Vanish (`normal`)** | Sinal de **"V" (paz e amor)** | Dissolução orgânica de cima para baixo com borda de plasma cintilante durante 3,6 segundos. |
| **`2`** | **Naruto Substitution (`naruto`)** | **Junte as duas palmas abertas** na frente do peito | **Kawarimi no Jutsu**: fumaça volumétrica e espirais estilo anime explodem com som sintetizado de fumaça e impacto na madeira (`naruto.wav`), enquanto um tronco de madeira gerado proceduralmente em código cai e quica no chão. |
| **`3`** | **Cosmic Particles (`particles`)** | Sinal de **"V" (paz e amor)** | Sua silhueta se desfaz em fragmentos coloridos e fagulhas luminosas levadas pelo vento em 2,15 segundos. |
| **`4`** | **Goku Teleport (`goku`)** | Encoste **indicador + médio juntos na testa** por 1,0s | **Transmissão Instantânea**: flash de Ki dourado, compressão espacial e linhas de velocidade estilo mangá/anime com som sintetizado de teletransporte (`goku.wav`); repita o gesto por 1,0s para reaparecer com o efeito reverso! |
| **`5`** | **Optical Stealth Cloak (`stealth`)** | Levante uma **mão aberta (5 dedos)** | Camuflagem óptica estilo Predador/Cyberpunk que refrata o fundo através da sua silhueta com borda holográfica neon. |
| **`6`** | **Dimensional Portal (`portal`)** | Gesto de **Rock / Chifres** (indicador + mindinho levantados) | Um vórtice de energia giratório se abre atrás de você, suga sua silhueta em espiral para o centro do portal e se fecha. |
| **`7`** | **Ninja Smoke Scroll (`smoke`)** | **Junte as duas palmas abertas** na frente do peito | Nuvem densa de fumaça acompanhada de um pergaminho ninja gerado proceduralmente que cai no seu lugar. |

Todos os efeitos contam com efeitos sonoros estéreo `.wav` sintetizados proceduralmente pelo módulo `ghostcam/audio.py` e gráficos gerados via código — sem depender de arquivos externos.

---

## 🚀 Como Começar

1. Dê um duplo clique em **`start_studio.bat`**.
2. Escolha o efeito inicial (`1` a `7`) na janela **GhostCam Studio**.
3. **Saia da frente da câmera por 4 segundos** enquanto o fundo vazio é capturado.
4. Volte para a frente da câmera e faça o gesto do efeito (ou aperte **`V`**)!

### Iniciar diretamente em um modo pelo terminal

```powershell
.\start_studio.bat --mode normal
.\start_studio.bat --mode naruto
.\start_studio.bat --mode particles
.\start_studio.bat --mode goku
.\start_studio.bat --mode stealth
.\start_studio.bat --mode portal
.\start_studio.bat --mode smoke
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

- **`1` a `7`**: Troca entre os 7 efeitos instantaneamente sem precisar fechar o programa.
- **`ESPAÇO`**: Captura um novo fundo vazio (saia da câmera por 4 segundos).
- **`V`**: Dispara manualmente o efeito de desaparecimento atual.
- **`R`**: Faz você reaparecer na câmera (com animação reversa nos modos Goku, Teletransporte, Camuflagem e Portal).
- **`F`**: Alterna tela cheia (fullscreen).
- **`Q` ou `ESC`**: Fecha o programa.

---

## 📜 Licença

Copyright (c) 2026 **Marcos W. Ferreira**.
Distribuído sob a licença **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)** — consulte o arquivo [LICENSE](LICENSE) para o texto integral.
