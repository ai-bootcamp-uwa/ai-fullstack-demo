import axios from "axios";
import { NextRequest, NextResponse } from "next/server";

// Extract plain text from assistant-ui message format
function extractTextFromMessage(content: any): string {
  if (typeof content === "string") return content;
  if (Array.isArray(content))
    return content
      .filter((item) => item.type === "text")
      .map((item) => item.text)
      .join(" ");
  if (content && typeof content === "object" && content.text)
    return content.text;
  const str = JSON.stringify(content);
  const match = str.match(/"text":"([^"]+)"/);
  return match ? match[1] : str;
}

export const runtime = "edge";
export const maxDuration = 30;

const BACKEND_GATEWAY_URL =
  process.env.BACKEND_GATEWAY_URL || "http://localhost:3003";

export async function POST(req: NextRequest) {
  try {
    const { messages } = await req.json();
    const lastMessage = messages[messages.length - 1];
    if (!lastMessage?.content) {
      throw new Error("No message content provided");
    }
    const authHeader =
      req.headers.get("authorization") ||
      "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1MzQzMDMyOH0.gAO2w2IB81Xp4WlYvDUS2CGa3gq6JP882RqIVVnNbR4";
    const messageText = extractTextFromMessage(lastMessage.content);
    // Generate consistent chat ID for this session
    const chatId = "geological-chat-" + Date.now();
    let response;
    try {
      // Attempt 1: Try sending message (chat might exist)
      response = await axios.post(
        `${BACKEND_GATEWAY_URL}/api/backend/chat`,
        {
          message: messageText,
          chat_id: chatId,
          include_context: false,
        },
        {
          headers: {
            Authorization: authHeader,
            "Content-Type": "application/json",
          },
          timeout: 25000,
        }
      );
    } catch (chatError) {
      // If chat not found, create it first
      if (axios.isAxiosError(chatError) && chatError.response?.status === 404) {
        // Create new chat
        const createResponse = await axios.post(
          `${BACKEND_GATEWAY_URL}/api/backend/chats`,
          {
            title: "Geological Chat",
            first_message: messageText,
          },
          {
            headers: {
              Authorization: authHeader,
              "Content-Type": "application/json",
            },
          }
        );
        // Use the actual chat ID returned from creation
        const actualChatId = createResponse.data.chat_id;
        // Now send message to the newly created chat
        response = await axios.post(
          `${BACKEND_GATEWAY_URL}/api/backend/chat`,
          {
            message: messageText,
            chat_id: actualChatId,
            include_context: false,
          },
          {
            headers: {
              Authorization: authHeader,
              "Content-Type": "application/json",
            },
            timeout: 25000,
          }
        );
      } else {
        throw chatError;
      }
    }
    const aiResponse =
      response.data.response || "Sorry, I couldn't process your request.";
    // Return streaming response for assistant-ui
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        const chunk = `0:"${aiResponse.replace(/"/g, '"')}"\n`;
        controller.enqueue(encoder.encode(chunk));
        controller.close();
      },
    });
    return new Response(stream, {
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });
  } catch (error) {
    console.error("Error in geological chat API:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
