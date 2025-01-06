## Signal-Equalizer 🎚️🎚️

This project develops a desktop application that functions as a signal equalizer. A signal equalizer is a tool used to adjust the balance of frequency components within a signal, allowing users to emphasize or attenuate specific frequency ranges. In this application, users can visually manipulate the magnitude of the frequency components of a signal using an intuitive interface, and reconstruct the modified signal for further analysis or playback. The equalizer provides both a graphical representation of the frequency spectrum and real-time feedback on the changes made.

## Features 🛠️
### Equalizer Modes 

* **Uniform Range Mode:** Splits the signal's frequency range into 10 equal sections, each adjustable via a slider.
  
    https://github.com/user-attachments/assets/4286dd31-4699-419e-a9e0-a2e4284a8d4c

* **Animal Sounds Mode:** Adjusts the magnitude of individual animal sounds within a mixed signal of four distinct animal sounds.
  
    https://github.com/user-attachments/assets/ae937760-2e28-47d4-b698-4801f101bbbf
  
* **Musical Instruments Mode:**  Adjusts the magnitude of specific musical instruments within a mixed signal containing four instruments.
    
    https://github.com/user-attachments/assets/b4ae987d-d6b0-43f2-b826-9e3773e05b12

* **ECG Signal Abnormalities:** Where each slider can control the magnitude of a specific abnormality (e.g. ECG arrhythmia) in the input biological signal.

    https://github.com/user-attachments/assets/5a784e1a-5e36-420b-9e58-c85aec20b0fe
* **Mixed Music and Animals Mode:**  Allows users to adjust the presence of different animal sounds and musical instruments within a mixed audio signal.

    https://github.com/user-attachments/assets/aecc5ec8-8971-4f48-8ede-19f80794dd8a
* **Mixed Vocals and Music Mode:** Allows users to adjust the levels of different vocals and musical elements within a song.

    https://github.com/user-attachments/assets/aad41067-adf4-4359-8b9a-1ce8d2fee8a0

* **Weiner Filter Mode:** Reduces noise from a sound signal by applying adaptive filtering techniques.

    https://github.com/user-attachments/assets/ec7add02-7196-4d29-9818-17a9991236de

### Other Features:

*   Sliders for adjusting frequency magnitudes of signal components.
*   Two linked cine signal viewers to display the input and output signals synchronously, with functionality for playback control, zoom, pan, and reset. 
*   Two spectrograms (one for input and one for output) that visually represent the frequency content of the signals. Spectrograms can be toggled on/off.
*   The ability to display the frequency range in either linear scale or Audiogram scale.

## Installation 📥

1. Clone this repository:
   ```bash
   git clone https://github.com/habibaalaa123/Beamforming_Simulator.git
   cd 2D-Beamforming-Simulator
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the simulator:
   ```bash
   python main.py
   ```

---

## Acknowledgments :
This project was supervised by Dr. Tamer Basha & Eng. Omar, who provided invaluable guidance and expertise throughout its development as a part of the Digital Signal Processing course at Cairo University Faculty of Engineering.

## Team Members
<div align="center">
  <table style="border-collapse: collapse; border: none;">
    <tr>
      <td align="center" style="border: none;">
        <img src="https://github.com/user-attachments/assets/b8b8ea9d-ccb6-4ad0-b900-8e48ef2113a8" alt="Enjy Ashraf" width="150" height="150"><br>
        <a href="https://github.com/enjyashraf18"><b>Enjy Ashraf</b></a>
      </td>
      <td align="center" style="border: none;">
        <img src="https://github.com/user-attachments/assets/5de3e403-7fce-4000-95d2-e9f07e0d78cf" alt="Nada Khaled" width="150" height="150"><br>
        <a href="https://github.com/NadaKhaled157"><b>Nada Khaled</b></a>
      </td>
      <td align="center" style="border: none;">
        <img src="https://github.com/user-attachments/assets/4b1f5180-2250-49ae-869f-4d00fb89447a" alt="Habiba Alaa" width="150" height="150"><br>
        <a href="https://github.com/habibaalaa123"><b>Habiba Alaa</b></a>
      </td>
      <td align="center" style="border: none;">
        <img src="https://github.com/user-attachments/assets/567fd220-acc8-4094-bfe0-5939a0048ca9" alt="Shahd Ahmed" width="150" height="150"><br>
        <a href="https://github.com/Shahd-A-Mahmoud"><b>Shahd Ahmed</b></a>
      </td>
    </tr>
  </table>
</div>
