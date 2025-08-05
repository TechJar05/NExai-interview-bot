// $(document).ready(function() {
//     // Update question count display
//     $('#numQuestions').on('input', function() {
//         $('#questionCount').text($(this).val());
//     });

//     // Audio recording variables
//     let mediaRecorder;
//     let audioChunks = [];
//     let audioBlob;
//     let interviewInProgress = false;
//     let audioContext;
//     let analyser;
//     let vadProcessor; // Assuming WebRTC VAD processor
//     let isVoiceDetected = false;

//     let lastActivityTime = Date.now();  // Track the last time voice was detected

//     // Initialize VAD
//     function initVAD() {
//         audioContext = new (window.AudioContext || window.webkitAudioContext)();
//         analyser = audioContext.createAnalyser();
//         analyser.fftSize = 256;
//         let bufferLength = analyser.frequencyBinCount;
//         let dataArray = new Uint8Array(bufferLength);

//         // WebRTC VAD - Assuming we have the VAD processor set up
//         vadProcessor = new WebRTCVoiceActivityDetector();
//         vadProcessor.setMode(3); // Set to "very sensitive" mode for detecting low voice levels
// // Mode 0: Very aggressive — detects speech with lower sensitivity (only loud speech).

// // Mode 1: Aggressive — works for normal speech.

// // Mode 2: Moderate — works for normal speech and quieter voices.

// // Mode 3: Very sensitive — detects even the faintest sounds of speech.
//         function checkForVoiceActivity() {
//             analyser.getByteFrequencyData(dataArray);
//             isVoiceDetected = vadProcessor.isSpeech(dataArray);

//             if (isVoiceDetected) {
//                 handleVoiceDetected(); // Handle when voice is detected
//             } else {
//                 handleSilenceDetected(); // Handle when silence is detected
//             }

//             requestAnimationFrame(checkForVoiceActivity);
//         }

//         checkForVoiceActivity();  // Start the VAD loop
//     }

//     // Handle when voice is detected
//     function handleVoiceDetected() {
//         lastActivityTime = Date.now();  // Reset inactivity timer
//         console.log("Voice detected...");
//         $('#micButton').addClass('recording');  // Change mic button state to indicate recording
//     }

//     // Handle when silence is detected
//     function handleSilenceDetected() {
//         if (Date.now() - lastActivityTime > 3000) {  // 3 seconds of silence before triggering action
//             console.log("Silence detected for too long...");
//             stopRecording();  // Stop recording when silence exceeds 3 seconds
//         }
//     }

//     // Start recording and initialize VAD
//     function startRecording() {
//         if (interviewInProgress) {
//             navigator.mediaDevices.getUserMedia({ audio: true })
//                 .then(stream => {
//                     const source = audioContext.createMediaStreamSource(stream);
//                     source.connect(analyser);
//                     initVAD();  // Initialize VAD for real-time speech detection

//                     mediaRecorder = new MediaRecorder(stream);
//                     mediaRecorder.ondataavailable = event => {
//                         audioChunks.push(event.data);
//                     };
//                     mediaRecorder.onstop = () => {
//                         audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
//                         uploadAudio();  // Upload audio when recording stops
//                     };
//                     mediaRecorder.start();
//                     console.log('Recording started...');
//                 })
//                 .catch(error => {
//                     console.error('Error accessing audio devices:', error);
//                 });
//         }
//     }


//     // Stop the recording when the interview ends or when manually stopped
//     function stopRecording() {
//         if (mediaRecorder) {
//             mediaRecorder.stop();
//             console.log('Recording stopped');
//         }
//     }

//     // Upload the audio file to the server after the recording ends
//     function uploadAudio() {
//         const formData = new FormData();
//         formData.append('audio', audioBlob);
//         formData.append('session_id', sessionStorage.getItem('session_id')); // or generate a unique session ID

//         fetch('/upload_audio', {
//             method: 'POST',
//             body: formData,
//         })
//         .then(response => response.json())
//         .then(data => {
//             if (data.status === 'success') {
//                 console.log('Audio uploaded successfully');
//             }
//         })
//         .catch(error => {
//             console.error('Error uploading audio:', error);
//         });
//     }

//     // Start interview
//     $('#startInterviewBtn').click(function() {
//         const role = $('#role').val();
//         const numQuestions = $('#numQuestions').val();
        
//         $(this).prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Starting...');
        
//         $.ajax({
//             url: 'interview/jobs/start_interview',
//             type: 'POST',
//             contentType: 'application/json',
//             data: JSON.stringify({
//                 role: role,
//                 num_questions: numQuestions
//             }),
//             success: function(response) {
//                 if (response.status === 'started') {
//                     $('.setup-section').hide();
//                     $('.interview-section').show();
//                     addMessage('bot', response.greeting);
//                     updateProgress(1, response.total_questions);
//                     getNextQuestion();
//                     interviewInProgress = true;  // Interview starts, so recording starts
//                     startRecording(); // Start audio recording when interview starts
//                 }
//             },
//             error: function(xhr) {
//                 alert('Error starting interview: ' + xhr.responseJSON?.message || 'Unknown error');
//             },
//             complete: function() {
//                 $('#startInterviewBtn').prop('disabled', false).html('<i class="fas fa-play"></i> Start Interview');
//             }
//         });
//     });

//     // Submit answer
//     $('#answerForm').submit(function(e) {
//         e.preventDefault();
//         const answer = $('#answerText').val().trim();
        
//         if (answer === '') {
//             alert('Please enter your answer');
//             return;
//         }
        
//         $('#submitAnswerBtn').prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Submitting...');

//         $.ajax({
//             url: 'interview/jobs/submit_answer',
//             type: 'POST',
//             contentType: 'application/json',
//             data: JSON.stringify({
//                 answer: answer
//             }),
//             success: function(response) {
//                 if (response.status === 'answer_submitted') {
//                     addMessage('user', answer);
//                     updateProgress(response.current_question, response.total_questions);
                    
//                     if (response.current_question < response.total_questions) {
//                         getNextQuestion();
//                     } else {
//                         generateReport();
//                     }
//                 }
//             },
//             error: function(xhr) {
//                 alert('Error submitting answer: ' + xhr.responseJSON?.message || 'Unknown error');
//             },
//             complete: function() {
//                 $('#submitAnswerBtn').prop('disabled', false).html('Submit Answer <i class="fas fa-paper-plane"></i>');
//                 $('#answerText').val('');
//             }
//         });
//     });

//     // Generate report
//     function generateReport() {
//         $('#generateReportBtn').prop('disabled', true).text('Generating...');

//         $.ajax({
//             url: '/report/generate_report',
//             type: 'POST',
//             success: function(response) {
//                 $('#generateReportBtn').prop('disabled', false).text('Generate Report');

//                 if (response.status === 'success') {
//                     if (!response.report || !response.report_filename) {
//                         alert("Incomplete report data received. Please try again.");
//                         return;
//                     }

//                     $('.interview-section').hide();
//                     $('.report-section').show();

//                     let summaryHtml = `
//                         <h4>Interview Results</h4>
//                         <div class="result-card mb-3 p-3 bg-light rounded">
//                             <div class="d-flex justify-content-between">
//                                 <span><strong>Overall Rating:</strong></span>
//                                 <span class="badge bg-primary">${response.avg_rating.toFixed(1)}/10</span>
//                             </div>
//                             <div class="d-flex justify-content-between mt-2">
//                                 <span><strong>Decision:</strong></span>
//                                 <span class="badge ${response.decision === 'SELECTED' ? 'bg-success' : 
//                                     response.decision === 'UNDER CONSIDERATION' ? 'bg-warning' : 'bg-danger'}">
//                                     ${response.decision}
//                                 </span>
//                             </div>
//                         </div>
//                         <h5 class="mt-4">Detailed Feedback</h5>
//                         <div class="feedback-text">${formatReportText(response.report)}</div>
//                     `;

//                     $('#reportSummary').html(summaryHtml);

//                     // Set up download button
//                     $('#downloadReportBtn').off('click').click(function() {
//                         window.location.href = `/download_report/${response.report_filename}`;
//                     });

//                 } else {
//                     alert('Report generation failed: ' + response.message);
//                 }
//             },
//             error: function(xhr) {
//                 $('#generateReportBtn').prop('disabled', false).text('Generate Report');
//                 let errorMsg = 'Unknown error';
//                 if (xhr.responseJSON && xhr.responseJSON.message) {
//                     errorMsg = xhr.responseJSON.message;
//                 } else if (xhr.responseText) {
//                     errorMsg = xhr.responseText;
//                 }
//                 alert('Error generating report: ' + errorMsg);
//                 console.error('🔴 Report Generation Failed:', errorMsg, xhr);
//             }
//         });
//     }

//     // Restart interview
//     $('#restartInterviewBtn').click(function() {
//         $('.report-section').hide();
//         $('.setup-section').show();
//         $('#conversationContainer').empty();
//         $.get('/', function() {
//             // Reload the page to reset everything
//             location.reload();
//         });
//     });

//     // Helper functions
//     function getNextQuestion() {
//         $.ajax({
//             url: '/jobs/interview/get_question',
//             type: 'GET',
//             success: function(response) {
//                 if (response.status === 'completed') {
//                     generateReport();
//                 } else if (response.text) {
//                     addMessage('bot', response.text);
//                 } else if (response.status === 'not_started') {
//                     alert('Interview not started. Please start the interview first.');
//                 }
//             },
//             error: function(xhr) {
//                 alert('Error getting question: ' + xhr.responseJSON?.message || 'Unknown error');
//             }
//         });
//     }

//     function addMessage(speaker, text) {
//         const messageClass = speaker === 'bot' ? 'bot-message' : 'user-message';
//         const icon = speaker === 'bot' ? '<i class="fas fa-robot me-2"></i>' : '<i class="fas fa-user me-2"></i>';
        
//         const messageHtml = `
//             <div class="message ${messageClass} d-flex">
//                 ${icon}
//                 <div>${text.replace(/\n/g, '<br>')}</div>
//             </div>
//         `;
        
//         $('#conversationContainer').append(messageHtml);
//         $('#conversationContainer').scrollTop($('#conversationContainer')[0].scrollHeight);
//     }

//     function formatReportText(text) {
//         return text.replace(/\n/g, '<br>') 
//                    .replace(/=== (.*?) ===/g, '<h5>$1</h5>') 
//                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
//     }
// });