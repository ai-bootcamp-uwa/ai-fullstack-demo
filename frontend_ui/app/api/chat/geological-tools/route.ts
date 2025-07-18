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
      return NextResponse.json(
        { error: 'No message content provided' },
        { status: 400 }
      );
    }

    // Get auth token from headers
    const authHeader = req.headers.get('authorization');
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }

    // Enhanced message with tool context
    const messageContent = typeof lastMessage.content === 'string' 
      ? lastMessage.content 
      : JSON.stringify(lastMessage.content);

    // Forward the chat request to Module 3 Backend Gateway with tools context
    const response = await axios.post(
      `${BACKEND_GATEWAY_URL}/api/backend/chat`,
      {
        message: messageContent,
        conversation_id: 'geological-chat-tools',
        tools_available: ['getSiteInfo', 'filterSites', 'getSiteGeometry'],
        context: 'geological_data_exploration'
      },
      {
        headers: {
          'Authorization': authHeader,
          'Content-Type': 'application/json'
        },
        timeout: 25000 // 25 seconds timeout
      }
    );

    // Return the AI response in the expected format
    return NextResponse.json({
      content: response.data.response || "Sorry, I couldn't process your request with the geological tools.",
      role: 'assistant'
    });

  } catch (error) {
    console.error('Error in geological tools chat API:', error);
    
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