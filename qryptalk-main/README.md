# QrypTalk: Quantum-Inspired Secure Messaging

## Project Overview

QrypTalk is a secure mobile messaging application developed for the Amaravati Quantum Valley Hackathon 2025. It serves as a proof-of-concept for quantum-resilient communication by implementing a high-fidelity software simulation of the BB84 Quantum Key Distribution (QKD) protocol. The application demonstrates how two users can establish a shared secret key with the ability to detect eavesdropping, and then use this key for end-to-end encrypted chat.

**Key Features:**

* **BB84 QKD Simulation:** Python backend uses Qiskit to simulate quantum key generation, including qubit preparation, measurement, and basis sifting.
* **Eavesdropper Detection:** Simulates an eavesdropper (Eve) and calculates the Quantum Bit Error Rate (QBER) to detect her presence. The system will abort key exchange if Eve is detected.
* **End-to-End Encryption:** Utilizes AES-GCM for symmetric encryption of chat messages once a secure key is established.
* **Real-time Security Status:** Android frontend dynamically displays connection security (Secure/Insecure), QBER, and enables/disables chat input based on key exchange outcome.
* **Modern Tech Stack:** Built with FastAPI (Python) for the backend and Kotlin/Jetpack Compose for a modern Android UI.

## System Architecture

QrypTalk operates on a client-server architecture:

* **Android Clients (Frontend):** Developed with Kotlin and Jetpack Compose, handling user interface, local message management, and secure communication with the backend via WebSockets.
* **FastAPI Server (Backend):** A Python-based asynchronous server that manages WebSocket connections, orchestrates the BB84 QKD simulation using Qiskit, and relays encrypted messages between clients.

## Getting Started

Follow these instructions to set up and run the QrypTalk application.

### Prerequisites

* **Python 3.8+** (for backend)
* **Java Development Kit (JDK) 11+** (for Android development)
* **Android Studio** (for Android frontend development)
* **Git** (for cloning the repository)

### 1. Clone the Repository

First, clone the project repository to your local machine:

```bash
git clone [https://github.com/harigs06/qryptalk.git](https://github.com/harigs06/qryptalk.git)
cd qryptalk
```

### 2. Backend Setup and Run

Navigate to the `backend` directory:

```bash
cd backend
```

#### One-Time Backend Setup:

1.  **Create a Virtual Environment:**
    ```bash
    python -m venv qkd_env
    ```
2.  **Activate the Virtual Environment:**
    * **Windows:**
        ```bash
        .\qkd_env\Scripts\Activate
        ```
    * **macOS/Linux:**
        ```bash
        source qkd_env/bin/activate
        ```
3.  **Install Required Python Packages:**
    ```bash
    pip install "qiskit[visualization]" qiskit-aer fastapi "uvicorn[standard]" numpy
    ```

#### Running the Backend Server:

1.  **Ensure your virtual environment is activated** (see step 2 above).
2.  **Run the FastAPI server:** This command starts the server and makes it accessible to other devices on your local network (like your Android phone).
    ```bash
    uvicorn bb84_server:app --reload --host 0.0.0.0
    ```
    * `--reload`: Automatically restarts the server when code changes are saved.
    * `--host 0.0.0.0`: **Crucial for mobile devices to connect.** This tells the server to listen on all available network interfaces, allowing your Android device to connect if it's on the same Wi-Fi network.

    The server will typically run on `http://0.0.0.0:8000`. Make a note of your computer's **local IP address** (e.g., `192.168.1.5`). You will need this for the Android app configuration.

### 3. Frontend (Android App) Setup and Run

Navigate back to the project root and then into the `QrypTalkAndroid' directory:

```bash
cd ..
cd QrypTalkAndroid
```

#### Android Studio Setup:

1.  **Open Android Studio:** Select "Open an existing Android Studio project" and navigate to the `qryptalk/QrypTalkAndroid` directory.
2.  **Sync Project:** Android Studio will prompt you to sync the project. Allow it to download any necessary Gradle dependencies.

#### Configure Backend IP Address:

1.  In Android Studio, open the file `app/src/main/java/com/example/qryptalk/MainActivity.kt`.
2.  Locate the `BASE_URL` constant.
3.  **Replace `YOUR_BACKEND_IP_ADDRESS`** with the local IP address of the machine running your Python backend server (e.g., `ws://192.168.1.5:8000/ws/`).

    ```kotlin
   
         val BASE_URL = "ws://YOUR_BACKEND_IP_ADDRESS:8000/ws/" // <--- CHANGE THIS!
   

#### Running the Android App:

1.  **Connect an Android Device or Start an Emulator:** In Android Studio, select your desired target device.
2.  **Run the App:** Click the "Run" button (green triangle) in Android Studio.

### Results and Outcomes
The QrypTalk prototype was systematically evaluated to validate its core functionalities: successful key generation in a secure environment and robust eavesdropper detection in a compromised one. The outcomes of these tests confirm that the application successfully implements the principles of the BB84 protocol.

Scenario 1: Secure Channel Simulation (Without Eavesdropper)

To validate the protocol's correctness and the application's baseline functionality, the simulation was configured with the eavesdropper_present flag set to False. Upon the connection of two clients, the backend server initiated the key exchange process. As documented in the backend logs (see Appendix, Figure A), the calculated Quantum Bit Error Rate (QBER) consistently measured at or near 0.0%. This result aligns with the theoretical expectation for an undisturbed quantum channel.

This negligible error rate correctly passed the 15% security threshold, leading to the successful generation of a final, shared secret key. The server then broadcast the key and a success status to both Android clients. Consequently, the application's UI, as shown in Figure 1, updated in real-time to reflect this outcome. It displayed a "Secure" status, a green lock icon, and the low QBER value. The message input field was enabled, allowing the two users to engage in a fully functional, end-to-end encrypted chat.

![WhatsApp Image 2025-10-12 at 16 20 38_57e85e0f](https://github.com/user-attachments/assets/0bf9e531-f9cf-49d7-ad02-35c20611b03c)
![WhatsApp Image 2025-10-12 at 16 17 11_4ed21776](https://github.com/user-attachments/assets/cea73176-e38d-43da-8408-dec13fb84982)



Scenario 2: Eavesdropper Detection Simulation

To validate the central security promise of the BB84 protocol, the simulation was then run with the eavesdropper_present flag set to True. This test was designed to demonstrate the system's ability to detect an active interception attempt. As predicted by quantum mechanics, the simulated eavesdropper's measurements introduced significant disturbances in the qubit states.

The backend logs show the QBER consistently measuring between 20% and 30%, a result that is in strong agreement with the theoretical error rate of ~25% expected under such an attack. This high QBER triggered the security protocol to abort the key exchange. The server correctly identified the channel as compromised, discarded the key, and sent a failure status to the clients. The mobile UI, shown in Figure 2, immediately reacted to this outcome. It displayed a prominent "Insecure" status with a red warning icon and the high QBER value. Critically, the message input field and send button were disabled, physically preventing any communication over the compromised channel.

Performance and Usability

Performance testing under a local Wi-Fi network environment showed that the entire key generation and verification process, from the second client's connection to the final key distribution, was completed with minimal latency, typically within 3-5 seconds. This demonstrates the solution's feasibility for real-time use in a practical application.

In summary, these results provide a comprehensive validation of our prototype. The system not only functions correctly as an end-to-end encrypted messaging application but, more importantly, successfully demonstrates the central security promise of the BB84 protocol.
![WhatsApp Image 2025-10-12 at 16 17 32_97475a1e](https://github.com/user-attachments/assets/f1ed6e8d-c5a8-428f-9564-0467722f0de1)
![WhatsApp Image 2025-10-12 at 16 21 21_e9156be8](https://github.com/user-attachments/assets/f2cdd4f8-7beb-4396-9216-ef8fb5aaa0e3)
![WhatsApp Image 2025-10-12 at 16 20 10_0bb9d44a](https://github.com/user-attachments/assets/42f4e942-6524-4430-81e8-5708889b841f)



## How to Use the Application

1.  **Start the Backend Server:** Ensure your Python backend is running as described above.
2.  **Run the Android App on Two Devices/Emulators:** To test the chat and key exchange, you will need two instances of the QrypTalk app running. This can be two physical Android phones, two emulators, or one of each.
3.  **Connect to the Server:** On each app instance, create/select a user. The app will attempt to connect to your backend server.
4.  **Initiate Key Exchange:** When two clients are successfully connected to the backend, the BB84 QKD simulation will automatically start on the server.
5.  **Observe Security Status:**
    * The top bar of the chat screen will display the connection status: "Secure" (green lock) or "Insecure" (red warning), along with the QBER value.
    * If the connection is "Secure" (QBER below threshold), the message input field will be enabled, and you can send encrypted messages.
    * If the connection is "Insecure" (QBER high, eavesdropper detected), the message input field will be disabled, indicating that the key exchange failed.
6.  **Simulate Eavesdropping (Backend Feature):**
    * To force an eavesdropping scenario, you can edit `bb84_server.py`. Find the line `generate_bb84_key, eavesdropper_present=True` and change `True` to `False` to simulate no eavesdropper, or vice-versa. Save the file; the backend will auto-reload.
    * Reconnect your Android apps to see the different QBER outcomes.

## Project Structure

```
qryptalk/
├── backend/
│   ├── bb84_server.py           # FastAPI server with BB84 simulation
│   ├── requirements.txt         # (Optional, but good practice for pip install)
│   └── qkd_env/                 # Python virtual environment
├── frontend/
│   ├── app/                     # Android application source
│   │   ├── src/
│   │   │   ├── main/
│   │   │   │   ├── java/com/example/qryptalk/
│   │   │   │   │   ├── MainActivity.kt
│   │   │   │   │   ├── models/
│   │   │   │   │   ├── network/ChatWebSocketManager.kt # <--- Configure IP here
│   │   │   │   │   ├── screens/
│   │   │   │   │   └── viewmodels/
│   │   ├── build.gradle
│   └── ...                      # Other Android project files
└── README.md
```

## Contributing

This project was created for the Amaravati Quantum Valley Hackathon 2025. Contributions and suggestions for further development (e.g., PQC integration, hardware interfacing) are welcome!


