// This file is responsible for IRIS UI

import { useEffect, useRef, useState } from 'react';
import './App.css';

function App() {

  // =========================================================
  // STATE
  // =========================================================

  // Stores whatever the user currently has in the text input
  const [message, setMessage] = useState('');

  // Stores the complete conversation displayed on the screen
  const [conversation, setConversation] = useState([]);

  // Tracks whether IRIS is currently processing a request
  const [loading, setLoading] = useState(false);

  // Tracks whether IRIS is currently listening through the microphone
  const [listening, setListening] = useState(false);

  // Tracks whether IRIS is currently speaking
  // Used to trigger the speaking animation on the orb
  const [speaking, setSpeaking] = useState(false);

  // Controls the current status of IRIS
  // Used to dynamically update the dashboard based on what IRIS is doing
  const [irisStatus, setIrisStatus] = useState('Ready');

  // Stores the current database connection status
  // Starts as "checking" until the backend reports the actual status
  const [databaseStatus, setDatabaseStatus] = useState('checking');

  // Stores the current backend connection status
  // Starts as "checking" until React receives a response from FastAPI
  const [backendStatus, setBackendStatus] = useState("checking");

  // Stores the current voice engine status
  // Starts as "checking" until the system health check determines its state
  const [voiceStatus, setVoiceStatus] = useState("checking");

  // Controls whether the IRIS startup animation is visible
  const [showStartup, setShowStartup] = useState(true);

  // Stores the activity messages displayed in the Activity panel
  // Initially shows that the frontend interface has been initialized
  const [activities, setActivities] = useState([
    "Interface initialized"
  ]);

  // Stores the activity messages displayed in the dashboard
  // This is separate from "activities" and is used by the addActivity() function
  const [activity, setActivity] = useState([
    'System initialized',
    'Backend connected',
    'Voice engine ready',
    'Awaiting your command...'
  ]);

  // Stores the current status of the individual IRIS system components
  // Used to display Backend, Database, and Voice Engine states on the dashboard
  const [systemStatus, setSystemStatus] = useState({
    backend: 'Checking...',
    database: 'Checking...',
    voice: 'Initializing...',
  });


  // =========================================================
  // REFERENCES
  // =========================================================

  // Points to the bottom of the conversation list
  // so the conversation can automatically scroll down
  const conversationEndRef = useRef(null);

  // Prevents the startup sequence from running more than once
  const startupRef = useRef(false);

  // Adds a new message to the Activity panel
  // Keeps only the most recent four activity messages visible
  const addActivity = (message) => {

    setActivity((prev) => [

      // Keeps the last three existing messages
      // and adds the new message as the fourth
      ...prev.slice(-3),

      message
    ]);
  };

  // Stores the previous backend status
  // Used to detect when the backend changes between
  // online and offline instead of repeatedly adding
  // the same activity message
  const previousBackendStatus = useRef(null);


  // =========================================================
  // IRIS STARTUP
  // =========================================================

  useEffect(() => {

    // Wait for the startup animation to finish
    if (showStartup) return;

    // Prevent the startup sequence from running more than once
    if (startupRef.current) return;

    startupRef.current = true;

    const startIRIS = async () => {

      try {

        // -------------------------------------------------------
        // IRIS STARTS SPEAKING
        // -------------------------------------------------------
        // The backend will generate and speak the startup
        // greeting using Edge TTS.

        setSpeaking(true);

        setIrisStatus('Speaking');

        addActivity('IRIS is speaking...');


        // -------------------------------------------------------
        // ASK BACKEND TO GENERATE STARTUP GREETING
        // -------------------------------------------------------

        const res = await fetch(
          'http://127.0.0.1:8000/api/voice/welcome',
          {
            method: 'POST'
          }
        );

        if (!res.ok) {
          throw new Error(
            `Startup greeting failed: ${res.status}`
          );
        }

        const data = await res.json();


        // -------------------------------------------------------
        // IRIS HAS FINISHED SPEAKING
        // -------------------------------------------------------

        setSpeaking(false);


        // Show the same greeting inside the conversation
        if (data.response) {

          setConversation([
            {
              role: 'iris',
              content: data.response,
            },
          ]);

        }


        // -------------------------------------------------------
        // START LISTENING
        // -------------------------------------------------------

        setIrisStatus('Ready');

        addActivity('Awaiting your command...');

        listenToUser();


      } catch (error) {

        // Make sure the orb does not remain stuck
        // in the speaking state if startup fails

        setSpeaking(false);

        setIrisStatus('Ready');

        console.error(
          "IRIS startup failed:",
          error
        );

      }

    };

    startIRIS();

  }, [showStartup]);


  // =========================================================
  // CONVERSATION AUTO-SCROLL
  // =========================================================

  useEffect(() => {

    conversationEndRef.current?.scrollIntoView({
      behavior: 'smooth',
    });

  }, [conversation]);


  // =========================================================
  // DYNAMIC SYSTEM HEALTH
  // =========================================================
  //
  // React periodically asks FastAPI for the current
  // system health.
  //
  // One request updates all system statuses:
  // Backend + Database + Voice + Activity
  // =========================================================

  useEffect(() => {

    const checkSystemHealth = async () => {

      try {

        const response = await fetch(
          'http://127.0.0.1:8000/api/health'
        );

        if (!response.ok) {
          throw new Error('Backend unavailable');
        }

        const data = await response.json();


        // =====================================================
        // BACKEND STATUS
        // =====================================================

        const currentBackendStatus =
          data.backend === 'online'
            ? 'online'
            : 'offline';

        setBackendStatus(currentBackendStatus);


        // =====================================================
        // DATABASE STATUS
        // =====================================================

        const currentDatabaseStatus =
          data.database === 'connected'
            ? 'connected'
            : 'disconnected';

        setDatabaseStatus(currentDatabaseStatus);


        // =====================================================
        // VOICE ENGINE STATUS
        // =====================================================
        // For now, the voice engine is considered ready
        // whenever the backend is online.

        const currentVoiceStatus =
          data.backend === 'online'
            ? 'ready'
            : 'offline';

        setVoiceStatus(currentVoiceStatus);


        // =====================================================
        // ACTIVITY PANEL
        // =====================================================
        // Only update the activity panel when the backend
        // actually changes state.

        if (
          previousBackendStatus.current !==
          currentBackendStatus
        ) {

          if (currentBackendStatus === 'online') {

            setActivities([
              'Interface initialized',
              'Backend connected',
              'Database connected',
              'Voice engine ready',
              'Awaiting your command...'
            ]);

          } else {

            setActivities([
              'Interface initialized',
              'Backend connection lost',
              'System offline'
            ]);
          }

          previousBackendStatus.current =
            currentBackendStatus;
        }

      } catch (error) {

        console.error(
          'System health check failed:',
          error
        );


        // =====================================================
        // IF FASTAPI CANNOT BE REACHED
        // =====================================================

        setBackendStatus('offline');
        setDatabaseStatus('disconnected');
        setVoiceStatus('offline');


        // Only update Activity if we weren't already offline.

        if (
          previousBackendStatus.current !==
          'offline'
        ) {

          setActivities([
            'Interface initialized',
            'Backend connection lost',
            'System offline'
          ]);

          previousBackendStatus.current =
            'offline';
        }
      }
    };


    // =========================================================
    // INITIAL CHECK
    // =========================================================

    checkSystemHealth();


    // =========================================================
    // CONTINUOUS CHECK
    // =========================================================
    // Recheck every 5 seconds so the dashboard can detect
    // backend/database changes without refreshing the page.

    const interval = setInterval(
      checkSystemHealth,
      5000
    );


    // =========================================================
    // CLEANUP
    // =========================================================
    // Stop the interval when App is unmounted.

    return () => clearInterval(interval);

  }, []);


  // =========================================================
  // SEND MESSAGE TO IRIS
  // =========================================================

  // This function is the main bridge between the React frontend
  // and the FastAPI backend.
  //
  // It can receive text from:
  //
  // 1. Microphone
  // 2. Text input
  // 3. Send button
  // 4. Enter key
  //
  // Everything eventually comes through this function.

  const sendMessage = async (text) => {

    // ---------------------------------------------------------
    // VALIDATION
    // ---------------------------------------------------------

    // Ignore empty messages
    // Also prevent another request while IRIS is already thinking
    if (!text.trim() || loading) return;

    // Remove unnecessary spaces from the message
    const userMessage = text.trim();


    // ---------------------------------------------------------
    // SHOW USER MESSAGE IMMEDIATELY
    // ---------------------------------------------------------

    setConversation((prev) => [
      ...prev,
      {
        role: 'user',
        content: userMessage,
      },
    ]);


    // Clear the text input
    setMessage('');


    // Tell the UI that IRIS is processing the request
    setLoading(true);


    // =========================================================
    // SEND REQUEST TO FASTAPI BACKEND
    // =========================================================

    try {

      const res = await fetch(
        'http://127.0.0.1:8000/api/chat',
        {
          method: 'POST',

          headers: {
            'Content-Type': 'application/json',
          },

          body: JSON.stringify({
            message: userMessage,
          }),
        }
      );


      // Convert the backend response from JSON
      const data = await res.json();


      // ---------------------------------------------------------
      // ADD IRIS RESPONSE TO CONVERSATION
      // ---------------------------------------------------------

      setConversation((prev) => [
        ...prev,
        {
          role: 'iris',
          content: data.response,
        },
      ]);


    } catch (error) {

      // ---------------------------------------------------------
      // BACKEND CONNECTION ERROR
      // ---------------------------------------------------------

      console.error(error);


      setConversation((prev) => [
        ...prev,
        {
          role: 'iris',
          content: 'Unable to connect to IRIS backend.',
        },
      ]);
    }


    // IRIS has finished processing
    setLoading(false);
  };


// =========================================================
// VOICE INPUT
// =========================================================

const listenToUser = async () => {

  try {

    // =======================================================
    // 1. IRIS STARTS LISTENING
    // =======================================================

    setListening(true);
    setSpeaking(false);

    setIrisStatus('Listening');

    addActivity('Listening for your command...');


    // =======================================================
    // 2. ASK BACKEND TO LISTEN
    // =======================================================

    const res = await fetch(
      'http://127.0.0.1:8000/api/voice',
      {
        method: 'POST',
      }
    );


    if (!res.ok) {
      throw new Error('Voice request failed');
    }


    const data = await res.json();


    // =======================================================
    // 3. NOTHING HEARD
    // =======================================================

    if (!data.heard) {

      setListening(false);
      setIrisStatus('Ready');

      listenToUser();

      return;
    }


    // =======================================================
    // 4. USER FINISHED SPEAKING
    // =======================================================

    setListening(false);

    setIrisStatus('Processing');

    addActivity('Command received');


    // Show user's command

    setConversation((prev) => [
      ...prev,
      {
        role: 'user',
        content: data.heard,
      },
    ]);


    // =======================================================
    // 5. STOP / EXIT
    // =======================================================

    const command =
      data.heard.toLowerCase().trim();


    if (
      command === 'stop' ||
      command === 'exit' ||
      command === 'sleep'
    ) {

      
      // IRIS starts speaking
      setSpeaking(true);
      setIrisStatus('Speaking');
      
      addActivity('IRIS is speaking...');
      
      // Speak the local standby response
      const speakResponse = await fetch(
        'http://127.0.0.1:8000/api/voice/speak?text=' +
        encodeURIComponent(data.response),
        {
          method: 'POST',
        }
      );
      
      if (!speakResponse.ok) {
        throw new Error('IRIS standby TTS failed');
      }
      
      await speakResponse.json();
      
      // IRIS finished speaking
      setSpeaking(false);
      setListening(false);
      
      setIrisStatus('Ready');
      setStandby(true);

      // Show IRIS's standby response
      setConversation((prev) => [
        ...prev,
        {
          role: 'iris',
          content: data.response,
        },
      ]);

      return;
    }

    // =======================================================
    // 6. IRIS RESPONSE
    // =======================================================

    if (data.response) {

      // =====================================================
      // IRIS STARTS SPEAKING
      // =====================================================
      setSpeaking(true);
      setIrisStatus('Speaking');
      addActivity('IRIS is speaking...');
      // =====================================================
      // IRIS SPEAKS THE RESPONSE
      // =====================================================
      const speakResponse = await fetch(
        'http://127.0.0.1:8000/api/voice/speak?text=' +
          encodeURIComponent(data.response),
        {
          method: 'POST',
        }
      );

      if (!speakResponse.ok) {
        throw new Error('IRIS TTS failed');
      }

      await speakResponse.json();

      // =====================================================
      // IRIS FINISHED SPEAKING
      // =====================================================
      setSpeaking(false);

      // =====================================================
      // NOW SHOW THE RESPONSE
      // =====================================================

      setConversation((prev) => [
        ...prev,
        {
          role: 'iris',
          content: data.response,
        },
      ]);
      setIrisStatus('Ready');

      addActivity('Awaiting your command...');
    }
    // =======================================================
    // 7. LISTEN AGAIN
    // =======================================================

    listenToUser();


  } catch (error) {

    console.error(
      'Voice command failed:',
      error
    );

    setSpeaking(false);
    setListening(false);

    setIrisStatus('Ready');
  }
};

  // =========================================================
  // USER INTERFACE
  // =========================================================

  return (
    <div className="iris-app">


      {/* =====================================================
          ANIMATED BACKGROUND
      ===================================================== */}

      <div
        className="energy-background"
        aria-hidden="true"
      >

        <svg
          viewBox="0 0 1600 900"
          preserveAspectRatio="none"
        >

          <defs>

            {/* Gradient used by the energy lines */}

            <linearGradient
              id="energyGradient"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="100%"
            >

              <stop
                offset="0%"
                stopColor="#00d9ff"
              />

              <stop
                offset="50%"
                stopColor="#4777ff"
              />

              <stop
                offset="100%"
                stopColor="#9b5cff"
              />

            </linearGradient>


            {/* Glow effect applied to energy lines */}

            <filter id="energyGlow">

              <feGaussianBlur
                stdDeviation="2.5"
                result="blur"
              />

              <feMerge>

                <feMergeNode in="blur" />

                <feMergeNode in="SourceGraphic" />

              </feMerge>

            </filter>

          </defs>


          {/* Top-left energy stream */}

          <path
            className="energy-line line-1"
            d="
              M -120 180
              C 120 20, 300 30, 480 100
              C 650 165, 760 230, 900 350
              C 1040 470, 1160 500, 1320 430
            "
          />


          {/* Top-right energy stream */}

          <path
            className="energy-line line-2"
            d="
              M 1900 120
              C 1640 0, 1480 30, 1300 110
              C 1130 185, 1020 250, 900 350
              C 780 450, 620 500, 470 430
            "
          />


          {/* Bottom-left energy stream */}

          <path
            className="energy-line line-3"
            d="
              M -120 760
              C 120 900, 300 850, 480 760
              C 650 675, 760 580, 900 470
              C 1040 360, 1160 350, 1320 420
            "
          />


          {/* Bottom-right energy stream */}

          <path
            className="energy-line line-4"
            d="
              M 1900 780
              C 1650 900, 1480 850, 1300 760
              C 1130 675, 1020 580, 900 470
              C 780 360, 620 350, 470 420
            "
          />


          {/* Additional upper energy stream */}

          <path
            className="energy-line line-5"
            d="
              M -150 420
              C 100 300, 280 250, 470 300
              C 650 350, 760 400, 900 350
              C 1040 300, 1180 180, 1380 80
            "
          />


          {/* Additional lower energy stream */}

          <path
            className="energy-line line-6"
            d="
              M 1750 480
              C 1500 600, 1320 650, 1130 600
              C 980 560, 850 500, 700 470
              C 540 440, 400 520, 220 700
            "
          />

        </svg>

      </div>


      {/* =====================================================
          HEADER
      ===================================================== */}

      <header className="iris-header">

        <div className="iris-brand">

          <h1>IRIS</h1>

          <span>
            An intelligent interactive AI system
          </span>

        </div>


        <div className="system-status">

          <span>
            ●
          </span>

          {backendStatus === "online"
            ? "SYSTEM ONLINE"
            : backendStatus === "checking"
            ? "SYSTEM CHECKING"
            : "SYSTEM OFFLINE"
          }

        </div>

      </header>
      
      {/* =========================================================
          IRIS STARTUP ANIMATION
      ========================================================= */}

      {showStartup && (
        <div className="startup-screen">

          <video
            autoPlay
            playsInline
            onEnded={() => setShowStartup(false)}
          >
            <source
              src="/iris-startup.mp4"
              type="video/mp4"
            />
          </video>

        </div>
      )}

      {/* =====================================================
          MAIN DASHBOARD
      ===================================================== */}

      <main className="dashboard">


        {/* ===================================================
            SYSTEM STATUS PANEL
        =================================================== */}

        <section className="panel left-panel">

          <h2>SYSTEM STATUS</h2>


          <div className="status-row">

            <span>Backend</span>

            <span
              className={
                backendStatus === "online"
                  ? "online"
                  : backendStatus === "checking"
                  ? "checking"
                  : "offline"
              }
            >

              ● {
                backendStatus === "online"
                  ? "Online"
                  : backendStatus === "checking"
                  ? "Checking..."
                  : "Offline"
              }

            </span>

          </div>


          <div className="status-row">

            <span>Database</span>

            <span
              className={
                databaseStatus === "connected"
                  ? "online"
                  : databaseStatus === "checking"
                  ? "checking"
                  : "offline"
              }
            >

              ● {
                databaseStatus === "connected"
                  ? "Connected"
                  : databaseStatus === "checking"
                  ? "Checking..."
                  : "Disconnected"
              }

            </span>

          </div>


          <div className="status-row">

            <span>Voice Engine</span>

            <span
              className={
                voiceStatus === "ready"
                  ? "online"
                  : voiceStatus === "checking"
                  ? "checking"
                  : "offline"
              }
            >

              ● {
                voiceStatus === "ready"
                  ? "Ready"
                  : voiceStatus === "checking"
                  ? "Initializing..."
                  : "Offline"
              }

            </span>

          </div>

        </section>


        {/* ===================================================
            IRIS CORE
        =================================================== */}

        <section className="iris-core-section">

          <div className="iris-core">


            {/* =================================================
                LISTENING SONAR
            =================================================
                Circular sonar waves appear when the user
                is speaking to IRIS.
            */}

            {listening && !speaking && (

              <>

                <div className="sonar-ring ring-1"></div>

                <div className="sonar-ring ring-2"></div>

                <div className="sonar-ring ring-3"></div>

              </>

            )}


            {/* =================================================
                IRIS SPEAKING WAVES
                ================================================= */}

            {speaking && (
              <svg
                className="iris-speaking-waves"
                viewBox="0 0 500 500"
                aria-hidden="true"
              >

                {/* =============================================
                    INNER CURLY RING
                    ============================================= */}

                <path
                  className="speaking-circle speaking-circle-1"
                  d="
                    M 250 145

                    C 270 138, 288 150, 295 168
                    C 302 186, 320 190, 335 180
                    C 350 170, 366 180, 370 198

                    C 374 216, 362 232, 370 248
                    C 378 265, 370 283, 352 290

                    C 334 297, 322 310, 316 328
                    C 310 346, 292 355, 275 346

                    C 258 337, 243 347, 226 350
                    C 207 353, 194 340, 193 321

                    C 192 302, 178 292, 163 282
                    C 148 272, 146 253, 158 239

                    C 170 225, 165 207, 158 190
                    C 151 173, 163 157, 181 155

                    C 200 153, 213 142, 230 148

                    C 237 151, 244 148, 250 145
                  "
                />


                {/* =============================================
                    MIDDLE CURLY RING
                    ============================================= */}

                <path
                  className="speaking-circle speaking-circle-2"
                  d="
                    M 250 105

                    C 278 96, 304 110, 315 136
                    C 326 161, 350 170, 373 157
                    C 396 144, 420 160, 418 187

                    C 416 212, 401 229, 414 250
                    C 427 272, 416 298, 391 306

                    C 366 314, 352 338, 343 362
                    C 334 386, 307 394, 287 376

                    C 267 358, 242 370, 220 382
                    C 198 394, 174 381, 173 356

                    C 172 331, 151 317, 130 304
                    C 109 291, 108 265, 126 248

                    C 144 231, 138 207, 129 184
                    C 120 161, 135 138, 160 137

                    C 185 136, 201 114, 224 112

                    C 234 111, 242 108, 250 105
                  "
                />


                {/* =============================================
                    OUTER CURLY RING
                    ============================================= */}

                <path
                  className="speaking-circle speaking-circle-3"
                  d="
                    M 250 65

                    C 285 52, 321 70, 336 102
                    C 351 134, 382 148, 414 131
                    C 446 114, 475 138, 468 172

                    C 461 206, 441 229, 458 256
                    C 475 283, 462 319, 428 329

                    C 394 339, 378 371, 366 404
                    C 354 437, 318 448, 292 423

                    C 266 398, 229 410, 199 428
                    C 169 446, 134 428, 134 393

                    C 134 358, 108 340, 80 323
                    C 52 306, 51 270, 75 249

                    C 99 228, 91 196, 78 166
                    C 65 136, 85 106, 118 108

                    C 151 110, 174 78, 205 79

                    C 222 80, 235 70, 250 65
                  "
                />

              </svg>
            )}


            {/* =================================================
                IRIS ORB
            ================================================= */}

            <img
              src="/iris-favicon.png"
              alt="IRIS"
              className={`iris-orb-image ${
                loading
                  ? 'iris-thinking'
                  : listening
                    ? 'iris-listening'
                    : speaking
                      ? 'iris-speaking'
                      : ''
              }`}
            />

          </div>


          <div className="iris-title">

            <span>I</span>

            <span>R</span>

            <span>I</span>

            <span>S</span>

          </div>


          <p>
            YOUR INTELLIGENT ASSISTANT
          </p>

        </section>


        {/* ===================================================
            ACTIVITY PANEL
        =================================================== */}

        <section className="panel activity-panel">

          <h2>ACTIVITY</h2>

          {activities.map((activity, index) => (

            <div
              className="activity-item"
              key={index}
            >

              <span>●</span>

              <span>{activity}</span>

            </div>

          ))}

        </section>


        {/* ===================================================
            CURRENT CONTEXT
        =================================================== */}

        <section className="panel left-panel">

          <h2>CURRENT CONTEXT</h2>

          <div className="status-row">

            <span>User</span>

            <span>Mandeep</span>

          </div>


          <div className="status-row">

            <span>Language</span>

            <span>English</span>

          </div>

        </section>


        {/* ===================================================
            VOICE PANEL
        =================================================== */}

        <section className="panel voice-panel">

          <h2>VOICE</h2>


          <button
            className={`microphone ${
              listening
                ? 'mic-active'
                : speaking
                  ? 'mic-speaking'
                  : ''
            }`}

            onClick={async () => {

              // Don't start another voice session
              // if IRIS is already listening
              if (listening) return;


              try {

                // -------------------------------------------------------
                // STEP 1: REACTIVATE IRIS
                // -------------------------------------------------------
                // The backend speaks:
                //
                // "Loading IRIS core."
                // "Hello again, Sir. What are we doing now?"
                //
                // Wait for the greeting to finish before
                // starting the microphone.

                setSpeaking(true);

                setIrisStatus('Speaking');

                addActivity('IRIS is speaking...');


                const res = await fetch(
                  'http://127.0.0.1:8000/api/voice/reactivate',
                  {
                    method: 'POST',
                  }
                );


                if (!res.ok) {

                  throw new Error(
                    `Voice reactivation failed: ${res.status}`
                  );

                }


                // Wait for the backend response
                await res.json();


                // -------------------------------------------------------
                // STEP 2: IRIS FINISHED SPEAKING
                // -------------------------------------------------------

                setSpeaking(false);


                // -------------------------------------------------------
                // STEP 3: START LISTENING
                // -------------------------------------------------------

                setIrisStatus('Ready');

                addActivity('Awaiting your command...');

                setListening(false);

                listenToUser();


              } catch (error) {

                console.error(
                  "IRIS voice reactivation failed:",
                  error
                );

                setSpeaking(false);

                setListening(false);

                setIrisStatus('Ready');

              }

            }}
          >

            🎙

          </button>


          <p>

            {speaking
              ? 'Speaking...'
              : listening
                ? 'Listening...'
                : 'Ready'
            }

          </p>

        </section>


        {/* ===================================================
            CONVERSATION PANEL
        =================================================== */}

        <section className="panel conversation-panel">

          <h2>CONVERSATION</h2>


          <div className="conversation-list">

            {/* Render every message currently stored
                inside the conversation state */}

            {conversation.map((msg, index) => (

              <div
                className={`message ${
                  msg.role === 'user'
                    ? 'user-message'
                    : 'iris-message'
                }`}
                key={index}
              >

                <div className="message-icon">

                  {msg.role === 'user'
                    ? '◉'
                    : '◉'}

                </div>


                <div>

                  <p>
                    <strong>
                      {msg.role === 'user' ? 'YOU:' : 'IRIS:'}
                    </strong>{' '}
                    {msg.content}
                  </p>

                </div>

              </div>

            ))}


            {/* Show this temporary message while IRIS
                is waiting for the backend response */}

            {loading && (

              <div className="message iris-message">

                <div className="message-icon">
                  ◉
                </div>

                <div>

                  <p>
                    IRIS is thinking...
                  </p>

                </div>

              </div>

            )}


            {/* Invisible reference used for automatic
                scrolling to the newest conversation message */}

            <div ref={conversationEndRef} />

          </div>

        </section>

      </main>


      {/* =====================================================
          INPUT / COMMAND COMPOSER
      ===================================================== */}

      <footer className="composer">

        {/* ===================================================
            TEXT INPUT
        =================================================== */}

        <input
          type="text"
          placeholder="Ask IRIS something..."
          value={message}

          // Update message state whenever the user types
          onChange={(e) => setMessage(e.target.value)}

          // Pressing Enter sends the message
          onKeyDown={(e) => {

            if (
              e.key === 'Enter' &&
              !e.shiftKey
            ) {

              e.preventDefault();

              e.currentTarget.parentElement
                .querySelector('.send-button')
                ?.click();

            }

          }}

        />


        {/* ===================================================
            SEND BUTTON
        =================================================== */}

        <button
          className="send-button"

          // Send whatever is currently in the text box
          onClick={() => sendMessage(message)}
        >

          ➤

        </button>

      </footer>

    </div>
  );
}


export default App;