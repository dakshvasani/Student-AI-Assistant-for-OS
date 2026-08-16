import { useState } from "react";
import "./App.css"; 

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");

  const askQuestion = async () => {
    if (!question.trim()) {
      return;
    }

    const userQuestion = question;

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        text: userQuestion,
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: userQuestion,
          history: messages,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong");
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text: data.answer,
          sources: data.sources || [],
        },
      ]);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text: "Sorry, something went wrong. Please try again.",
        },
      ]);

      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askQuestion();
    }
  };

  const uploadPDF = async () => {

  if (!selectedFile) {
    setUploadMessage("Please select a PDF first.");
    return;
  }

  setUploading(true);
  setUploadMessage("Processing PDF...");

  const formData = new FormData();

  formData.append(
    "file",
    selectedFile
  );

  try {

    const response = await fetch(
      "http://127.0.0.1:8000/upload",
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Upload failed"
      );
    }

    setUploadMessage(
      `✅ ${data.filename} processed successfully. ${data.chunks} chunks created.`
    );

  } catch (error) {

    console.error(error);

    setUploadMessage(
      "❌ Failed to process PDF."
    );

  } finally {

    setUploading(false);
  }
};

  return (
    <div className="app">
      <div className="chat-container">

        <header className="header">
          <div className="logo">🎓</div>

          <div>
            <h1>Student AI Assistant</h1>
            <p>Learn smarter with GenAI</p>
          </div>
        </header>

        <main className="messages">
          <div className="upload-section">

            <label>
              📄 Upload Study PDF
            </label>
            
            <div className="upload-controls">
            
              <input
                type="file"
                accept=".pdf"
                onChange={(event) =>
                  setSelectedFile(
                    event.target.files[0]
                  )
                }
              />
          
              <button
                onClick={uploadPDF}
                disabled={uploading}
              >
                {uploading
                  ? "Processing..."
                  : "Upload PDF"}
              </button>
                
            </div>
                
            {uploadMessage && (
              <p className="upload-message">
                {uploadMessage}
              </p>
            )}
          
          </div>

          {messages.length === 0 && (
            <div className="welcome">
              <h2>👋 Hello Student!</h2>

              <p>
                Ask me about your studies, programming,
                academic concepts, or learning materials.
              </p>

              <div className="examples">
                <button
                  onClick={() =>
                    setQuestion("Explain artificial intelligence simply")
                  }
                >
                  Explain AI
                </button>

                <button
                  onClick={() =>
                    setQuestion("What is cloud computing?")
                  }
                >
                  Explain Cloud Computing
                </button>

                <button
                  onClick={() =>
                    setQuestion("Explain Python functions with an example")
                  }
                >
                  Learn Python
                </button>
              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.role}`}
            >
              <div className="message-label">
                {message.role === "user" ? "You" : "AI Assistant"}
              </div>

              <div className="message-text">
                {message.text}
                        
                {message.role === "assistant" &&
                  message.sources &&
                  message.sources.length > 0 && (
                    <div className="sources">
                      <strong>📚 Sources</strong>
                  
                      {message.sources.map((source) => (
                        <div
                          key={source.chunk_id}
                          className="source-item"
                        >
                          Operating System — Section{" "}
                          {source.chunk_id}
                          {" "}({source.similarity})
                        </div>
                      ))}
                    </div>
                  )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="message assistant">
              <div className="message-label">
                AI Assistant
              </div>

              <div className="message-text">
                Thinking...
              </div>
            </div>
          )}

        </main>

        <div className="input-area">

          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask your question..."
            rows="2"
          />

          <button
            className="send-button"
            onClick={askQuestion}
            disabled={loading}
          >
            {loading ? "..." : "Send"}
          </button>

        </div>

        <footer>
          Powered by Google Gemini
        </footer>

      </div>
    </div>
  );
}

export default App;