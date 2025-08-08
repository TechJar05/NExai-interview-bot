// $(document).ready(function() {
//     // Update question count display
//     $('#numQuestions').on('input', function() {
//         $('#questionCount').text($(this).val());
//     });

//     // Start interview
//     $('#startInterviewBtn').click(function() {
//         const role = $('#role').val();
//         const numQuestions = $('#numQuestions').val();
        
//         $(this).prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Starting...');
        
//         $.ajax({
//             url: '/ibot/interview/start_interview',
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
//             url: '/ibot/interview/submit_answer',
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

//     // Record audio button
//     $('#recordBtn').click(function() {
//         $(this).prop('disabled', true).html('<i class="fas fa-microphone-alt-slash"></i> Recording...');

//         startRecording();
//     });

//     // Start recording and send audio data to backend
//     let mediaRecorder;
//     let audioChunks = [];

//     function startRecording() {
//         console.log("Recording started...");

//         navigator.mediaDevices.getUserMedia({ audio: true })
//             .then(function(stream) {
//                 mediaRecorder = new MediaRecorder(stream);

//                 mediaRecorder.ondataavailable = function(event) {
//                     audioChunks.push(event.data);
//                 };

//                 mediaRecorder.onstop = function() {
//                     const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
//                     const reader = new FileReader();

//                     reader.onloadend = function() {
//                         // Log base64 audio data for debugging purposes
//                         console.log("Base64 audio data generated:", reader.result);

//                         // Send the base64-encoded audio data to the backend
//                         sendAudioToBackend(reader.result);
//                     };

//                     reader.readAsDataURL(audioBlob);
//                 };

//                 mediaRecorder.start();
//             })
//             .catch(function(error) {
//                 console.error("Error starting audio recording:", error);
//             });
//     }

//     function stopRecording() {
//         console.log("Recording stopped...");
//         mediaRecorder.stop();
//     }

//     // Send audio data to the backend
//     function sendAudioToBackend(base64AudioData) {
//         console.log("Sending audio data to backend...");

//         $.ajax({
//             url: '/ibot/interview/submit_answer',
//             type: 'POST',
//             contentType: 'application/json',
//             data: JSON.stringify({
//                 answer: 'Audio Answer',  // Replace with the actual answer if needed
//                 audio_data: base64AudioData,  // Send the base64-encoded audio data
//             }),
//             success: function(response) {
//                 console.log("Backend response:", response);
//                 // Handle response (e.g., feedback, next question, etc.)
//             },
//             error: function(xhr) {
//                 console.error("Error sending audio:", xhr);
//             }
//         });
//     }

//     // Generate report
//     function generateReport() {
//         $('#generateReportBtn').prop('disabled', true).text('Generating...');

//         $.ajax({
//             url: '/ibot/interview/generate_report/',
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
//             url: '/ibot/interview/get_question',
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


































$(document).ready(function() {
    // Update question count display
    $('#numQuestions').on('input', function() {
        $('#questionCount').text($(this).val());
    });

    // Start interview
    $('#startInterviewBtn').click(function() {
        const role = $('#role').val();
        const numQuestions = $('#numQuestions').val();
        
        $(this).prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Starting...');
        
        $.ajax({
            url: '/ibot/interview/start_interview',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                role: role,
                num_questions: numQuestions
            }),
            success: function(response) {
                if (response.status === 'started') {
                    $('.setup-section').hide();
                    $('.interview-section').show();
                    addMessage('bot', response.greeting);
                    updateProgress(1, response.total_questions);
                    getNextQuestion();
                }
            },
            error: function(xhr) {
                alert('Error starting interview: ' + xhr.responseJSON?.message || 'Unknown error');
            },
            complete: function() {
                $('#startInterviewBtn').prop('disabled', false).html('<i class="fas fa-play"></i> Start Interview');
            }
        });
    });

    // Submit answer
    $('#answerForm').submit(function(e) {
        e.preventDefault();
        const answer = $('#answerText').val().trim();
        
        if (answer === '') {
            alert('Please enter your answer');
            return;
        }
        
        $('#submitAnswerBtn').prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Submitting...');
        
        $.ajax({
            url: '/ibot/interview/submit_answer',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                answer: answer
            }),
            success: function(response) {
                if (response.status === 'answer_submitted') {
                    addMessage('user', answer);
                    updateProgress(response.current_question, response.total_questions);
                    
                    if (response.current_question < response.total_questions) {
                        getNextQuestion();
                    } else {
                        generateReport();
                    }
                }
            },
            error: function(xhr) {
                alert('Error submitting answer: ' + xhr.responseJSON?.message || 'Unknown error');
            },
            complete: function() {
                $('#submitAnswerBtn').prop('disabled', false).html('Submit Answer <i class="fas fa-paper-plane"></i>');
                $('#answerText').val('');
            }
        });
    });

    // Record audio button
    $('#recordBtn').click(function() {
        $(this).prop('disabled', true).html('<i class="fas fa-microphone-alt-slash"></i> Recording...');

        startRecording();
    });

    // Start recording and send audio data to backend
    let mediaRecorder;
    let audioChunks = [];

    function startRecording() {
        console.log("Recording started...");

        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(function(stream) {
                mediaRecorder = new MediaRecorder(stream);

                mediaRecorder.ondataavailable = function(event) {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = function() {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const reader = new FileReader();

                    reader.onloadend = function() {
                        // Log base64 audio data for debugging purposes
                        console.log("Base64 audio data generated:", reader.result);

                        // Send the base64-encoded audio data to the backend
                        sendAudioToBackend(reader.result);
                    };

                    reader.readAsDataURL(audioBlob);
                };

                mediaRecorder.start();
            })
            .catch(function(error) {
                console.error("Error starting audio recording:", error);
            });
    }

    function stopRecording() {
        console.log("Recording stopped...");
        mediaRecorder.stop();
    }

    // Send audio data to the backend
    function sendAudioToBackend(base64AudioData) {
        console.log("Sending audio data to backend...");

        $.ajax({
            url: '/ibot/interview/submit_answer',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                answer: 'Audio Answer',  // Replace with the actual answer if needed
                audio_data: base64AudioData,  // Send the base64-encoded audio data
            }),
            success: function(response) {
                console.log("Backend response:", response);
                // Handle response (e.g., feedback, next question, etc.)
            },
            error: function(xhr) {
                console.error("Error sending audio:", xhr);
            }
        });
    }

    // Generate report
    function generateReport() {
        $('#generateReportBtn').prop('disabled', true).text('Generating...');

        $.ajax({
            url: '/ibot/interview/generate_report/',
            type: 'POST',
            success: function(response) {
                $('#generateReportBtn').prop('disabled', false).text('Generate Report');

                if (response.status === 'success') {
                    if (!response.report || !response.report_filename) {
                        alert("Incomplete report data received. Please try again.");
                        return;
                    }

                    $('.interview-section').hide();
                    $('.report-section').show();

                    let summaryHtml = `
                        <h4>Interview Results</h4>
                        <div class="result-card mb-3 p-3 bg-light rounded">
                            <div class="d-flex justify-content-between">
                                <span><strong>Overall Rating:</strong></span>
                                <span class="badge bg-primary">${response.avg_rating.toFixed(1)}/10</span>
                            </div>
                            <div class="d-flex justify-content-between mt-2">
                                <span><strong>Decision:</strong></span>
                                <span class="badge ${response.decision === 'SELECTED' ? 'bg-success' : 
                                    response.decision === 'UNDER CONSIDERATION' ? 'bg-warning' : 'bg-danger'}">
                                    ${response.decision}
                                </span>
                            </div>
                        </div>
                        <h5 class="mt-4">Detailed Feedback</h5>
                        <div class="feedback-text">${formatReportText(response.report)}</div>
                    `;

                    $('#reportSummary').html(summaryHtml);

                    // Set up download button
                    $('#downloadReportBtn').off('click').click(function() {
                        window.location.href = `/download_report/${response.report_filename}`;
                    });

                } else {
                    alert('Report generation failed: ' + response.message);
                }
            },
            error: function(xhr) {
                $('#generateReportBtn').prop('disabled', false).text('Generate Report');
                let errorMsg = 'Unknown error';
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    errorMsg = xhr.responseJSON.message;
                } else if (xhr.responseText) {
                    errorMsg = xhr.responseText;
                }
                alert('Error generating report: ' + errorMsg);
                console.error('🔴 Report Generation Failed:', errorMsg, xhr);
            }
        });
    }

    // Restart interview
    $('#restartInterviewBtn').click(function() {
        $('.report-section').hide();
        $('.setup-section').show();
        $('#conversationContainer').empty();
        $.get('/', function() {
            // Reload the page to reset everything
            location.reload();
        });
    });

    // Helper functions
    function getNextQuestion() {
        $.ajax({
            url: '/ibot/interview/get_question',
            type: 'GET',
            success: function(response) {
                if (response.status === 'completed') {
                    generateReport();
                } else if (response.text) {
                    addMessage('bot', response.text);
                } else if (response.status === 'not_started') {
                    alert('Interview not started. Please start the interview first.');
                }
            },
            error: function(xhr) {
                alert('Error getting question: ' + xhr.responseJSON?.message || 'Unknown error');
            }
        });
    }

    function addMessage(speaker, text) {
        const messageClass = speaker === 'bot' ? 'bot-message' : 'user-message';
        const icon = speaker === 'bot' ? '<i class="fas fa-robot me-2"></i>' : '<i class="fas fa-user me-2"></i>';
        
        const messageHtml = `
            <div class="message ${messageClass} d-flex">
                ${icon}
                <div>${text.replace(/\n/g, '<br>')}</div>
            </div>
        `;
        
        $('#conversationContainer').append(messageHtml);
        $('#conversationContainer').scrollTop($('#conversationContainer')[0].scrollHeight);
    }

    function formatReportText(text) {
        return text.replace(/\n/g, '<br>')
                   .replace(/=== (.*?) ===/g, '<h5>$1</h5>')
                   .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }
});
