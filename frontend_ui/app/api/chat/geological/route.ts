import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';

export const runtime = "edge";
export const maxDuration = 30;

// Backend Gateway URL
const BACKEND_GATEWAY_URL = process.env.BACKEND_GATEWAY_URL || 'http://localhost:3003';

export async function POST(req: NextRequest) {
  try {
    const { messages } = await req.json();
    
    // Get the last message from the conversation
    const lastMessage = messages[messages.length - 1];
    if (!lastMessage?.content) {
      throw new Error('No message content provided');
    }

    // Get auth token from headers (use fresh token for testing)
    const authHeader = req.headers.get('authorization') || 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1MjkxMzkyNX0.OE-rGhmlo95-aZYJA9_oF_CxqVmZLikJzkEfsZOOp1M';

    // Get response from our backend
    const response = await axios.post(
      `${BACKEND_GATEWAY_URL}/api/backend/chat`,
      {
        message: typeof lastMessage.content === 'string' 
          ? lastMessage.content 
          : JSON.stringify(lastMessage.content),
        conversation_id: 'geological-chat'
      },
      {
        headers: {
          'Authorization': authHeader,
          'Content-Type': 'application/json'
        },
        timeout: 25000 // 25 seconds timeout
      }
    );

    const aiResponse = response.data.response || "Sorry, I couldn't process your request.";

    // Create a proper streaming response for assistant-ui
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        // Send the response in the format expected by assistant-ui
        const chunk = `0:"${aiResponse.replace(/"/g, '\\"')}"\n`;
        controller.enqueue(encoder.encode(chunk));
        controller.close();
      },
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });

  } catch (error) {
    console.error('Error in geological chat API:', error);
    
    // Handle different error types
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 401) {
        return NextResponse.json(
          { error: 'Authentication failed' },
          { status: 401 }
        );
      }
      if (error.response?.status === 503) {
        return NextResponse.json(
          { error: 'AI service temporarily unavailable' },
          { status: 503 }
        );
      }
      if (error.code === 'ECONNREFUSED') {
        return NextResponse.json(
          { error: 'Backend service unavailable' },
          { status: 503 }
        );
      }
    }
    
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 