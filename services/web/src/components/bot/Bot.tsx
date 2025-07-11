/*
 *
 * Licensed under the Apache License, Version 2.0 (the “License”);
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *         http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an “AS IS” BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import React, { useState, useEffect } from "react";

import config from "./config";
import { APIService } from "../../constants/APIConstant";
import MessageParser, { ChatMessage } from "./MessageParser";
import ActionProvider from "./ActionProvider";
import Chatbot, { createChatBotMessage } from "react-chatbot-kit";
import { Row, Col } from "antd";
import { Space } from "antd";
import Icon, {
  CloseSquareOutlined,
  DeleteOutlined,
  ExpandAltOutlined,
  WechatWorkOutlined,
} from "@ant-design/icons";
import "./chatbot.css";

const superagent = require("superagent");

const PandaSvg = (): JSX.Element => (
  <svg viewBox="0 0 512 512" width="1em" height="1em" fill="currentColor">
    <path
      d="M437.333,21.355H74.667C33.493,21.355,0,54.848,0,96.021v213.333c0,41.173,33.493,74.667,74.667,74.667h48.256    l-36.821,92.032c-1.771,4.395-0.405,9.429,3.328,12.352c1.92,1.515,4.245,2.283,6.592,2.283c2.176,0,4.352-0.661,6.208-1.984    l146.56-104.683h188.587c41.173,0,74.667-33.493,74.667-74.667V96.021C512,54.848,478.507,21.355,437.333,21.355z"
      fill="#1890FF"
    />
  </svg>
);

const ChatIcon = ({ size = "26pt" }: { size?: string | number }) => (
  <WechatWorkOutlined style={{ fontSize: size }} />
);

interface ChatBotState {
  openapiKey: string | null;
  initializing: boolean;
  initializationRequired: boolean;
  accessToken: string;
  isLoggedIn: boolean;
  role: string;
  messages: ChatMessage[]; // ChatBotMessage[] or IMessage[]
}

interface ChatBotComponentProps {
  accessToken: string;
  isLoggedIn: boolean;
  role: string;
}

const ChatBotComponent: React.FC<ChatBotComponentProps> = (props) => {
  // Expanded state for chatbot container
  const [expanded, setExpanded] = useState<boolean>(false);
  // Set to true so chatbot is open on UI load
  const [showBot, toggleBot] = useState<boolean>(true);

  const [chatbotState, setChatbotState] = useState<ChatBotState>({
    openapiKey: localStorage.getItem("openapi_key"),
    initializing: false,
    initializationRequired: false,
    accessToken: props.accessToken,
    isLoggedIn: props.isLoggedIn,
    role: props.role,
    messages: [],
  });

  const headerText = (): JSX.Element => {
    return (
      <div
        style={{
          backgroundColor: "#04AA6D",
          color: "white",
          padding: "1px",
          borderRadius: "1px",
        }}
      >
        <Space style={{ margin: "5px" }}>
          &nbsp; &nbsp; Exploit CrapBot &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;
          &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;
          &nbsp;
          <button
            className="expand-chatbot-btn"
            style={{ position: "absolute", top: 10, right: 35, zIndex: 1100 }}
            onClick={() => setExpanded((prev) => !prev)}
            aria-label={expanded ? "Collapse Chatbot" : "Expand Chatbot"}
          >
            <ExpandAltOutlined />
          </button>
          <button
            className="toggle-chatbot-btn"
            style={{ position: "absolute", top: 10, right: 10, zIndex: 1100 }}
            onClick={() => toggleBot((prev) => !prev)}
            aria-label={showBot ? "Hide Chatbot" : "Show Chatbot"}
          >
            <CloseSquareOutlined />
          </button>
        </Space>
      </div>
    );
  };

  useEffect(() => {
    const fetchInit = async () => {
      const stateUrl = APIService.CHATBOT_SERVICE + "genai/state";
      let initRequired = false;
      let chatHistory: ChatMessage[] = [];
      // Wait for the response
      await superagent
        .get(stateUrl)
        .set("Accept", "application/json")
        .set("Content-Type", "application/json")
        .set("Authorization", `Bearer ${props.accessToken}`)
        .then((res: any) => {
          console.log("I response:", res.body);
          if (res.status === 200) {
            if (res.body?.initialized === "true") {
              initRequired = false;
              if (res.body?.chat_history) {
                chatHistory = res.body?.chat_history;
                setChatbotState((prev) => ({
                  ...prev,
                  messages: chatHistory.map((msg) => ({
                    role: msg.role,
                    content: msg.content,
                    id: msg.id,
                  })),
                }));
              }
            } else {
              initRequired = true;
            }
          }
        })
        .catch((err: any) => {
          console.log("Error prefetch: ", err);
        });
      console.log("Initialization required:", initRequired);
      setChatbotState((prev) => ({
        ...prev,
        initializationRequired: initRequired,
      }));
    };
    fetchInit();
  }, []);

  const config_chatbot = {
    ...config,
    customComponents: {
      header: headerText,
      botAvatar: () => (
        <Icon
          component={PandaSvg}
          className="app-chatbot-button-icon"
          style={{ fontSize: "40", color: "white" }}
        />
      ),
      customButtons: (
        <button
          className="expand-chatbot-btn"
          style={{ position: "absolute", top: 10, right: 10, zIndex: 1100 }}
          onClick={() => setExpanded((prev) => !prev)}
          aria-label={expanded ? "Collapse Chatbot" : "Expand Chatbot"}
        >
          ⤢
        </button>
      ),
    },
    state: chatbotState,
  };

  // Convert ChatMessage[] to IMessage[] for UI
  const chatMessagesToIMessages = (messages: ChatMessage[]): IMessage[] =>
    messages.map((msg) => ({
      id: msg.id,
      message: msg.content,
      type: msg.role === "assistant" ? "bot" : "user",
    }));

  // Dynamic initialMessages state
  const [initialMessages, setInitialMessages] = useState<any[] | null>(null);

  useEffect(() => {
    async function fetchHistory() {
      const history = await fetchChatHistoryFromBackend(); // returns ChatMessage[]
      setInitialMessages(
        history.length > 0
          ? history.map((msg) => createChatBotMessage(msg.content, {}))
          : [
              createChatBotMessage(
                `Hi, Welcome to crAPI! I'm CrapBot, and I'm here to be exploited.`,
                {},
              ),
            ],
      );
    }
    fetchHistory();
  }, []);

  // Debug: log messages before rendering
  console.log("messages for UI:", chatbotState.messages);

  // Canonical message type is ChatMessage (imported above)

  // Define IMessage for react-chatbot-kit compatibility
  interface IMessage {
    id: number;
    message: string;
    type: string; // required
  }

  // Remount Chatbot only on clear, reset, or init
  const [chatbotInstanceKey, setChatbotInstanceKey] = useState(0);

  // Convert ChatMessage[] (backend/state) <-> IMessage[] (UI)
  const chatHistoryToIMessage = (history: ChatMessage[]): IMessage[] =>
    history.map((msg, idx) => ({
      id: idx, // number, not string
      message: msg.content,
      type: msg.role === "assistant" ? "bot" : "user", // always string
    }));

  // Use ChatMessage for all state/history updates
  const addResponseMessage = (message: ChatMessage): void => {
    setChatbotState((state) => ({
      ...state,
      messages: [...state.messages, message],
    }));
  };

  // Fetch chat history from backend
  const fetchChatHistoryFromBackend = async (): Promise<ChatMessage[]> => {
    try {
      const res = await superagent
        .get(APIService.CHATBOT_SERVICE + "genai/history")
        .set("Accept", "application/json")
        .set("Content-Type", "application/json")
        .set("Authorization", `Bearer ${props.accessToken}`);
      console.log("Fetched chat history:", res.body);
      return res.body?.chat_history || [];
    } catch (err) {
      console.error("Failed to fetch chat history from backend", err);
      return [];
    }
  };

  // Save messages to backend and re-fetch
  const saveMessages = (messages: IMessage[]): void => {
    // Update UI state immediately (optimistic UI)
    setChatbotState((prev) => ({
      ...prev,
      messages: iMessageToChatHistory(messages),
    }));

    // Sync with backend in the background
    (async () => {
      const chatHistory = iMessageToChatHistory(messages);
      try {
        await superagent
          .get(APIService.CHATBOT_SERVICE + "genai/state")
          .set("Accept", "application/json")
          .set("Content-Type", "application/json")
          .set("Authorization", `Bearer ${props.accessToken}`)
          .send({ chat_history: chatHistory });
        // Do NOT re-fetch or remount here!
      } catch (err) {
        console.error("Failed to save chat history to backend", err);
      }
    })();
  };

  // IMessage for react-chatbot-kit UI
  interface IMessage {
    id: number;
    message: string;
    type: string; // "bot" or "user"
  }

  // Convert IMessage[] (UI) to ChatMessage[] (backend)
  const iMessageToChatHistory = (messages: IMessage[]): ChatMessage[] =>
    messages.map((msg) => ({
      role: msg.type === "bot" ? "assistant" : "user",
      content: msg.message,
      id: msg.id,
    }));

  const loadMessages = (): IMessage[] | undefined => {
    const msgs = chatHistoryToIMessage(chatbotState.messages);
    return msgs.length > 0 ? msgs : undefined;
  };

  const clearHistory = async (): Promise<void> => {
    try {
      await superagent
        .get(APIService.CHATBOT_SERVICE + "genai/state")
        .set("Accept", "application/json")
        .set("Content-Type", "application/json")
        .set("Authorization", `Bearer ${props.accessToken}`)
        .send({ chat_history: [] });
      const latestHistory = await fetchChatHistoryFromBackend();
      setChatbotState((prev) => ({
        ...prev,
        messages: latestHistory,
      }));
      setChatbotInstanceKey((prev) => prev + 1);
    } catch (err) {
      console.error("Failed to clear chat history on backend", err);
    }
  };

  const resetHistory = async (): Promise<void> => {
    try {
      await superagent
        .get(APIService.CHATBOT_SERVICE + "genai/state")
        .set("Accept", "application/json")
        .set("Content-Type", "application/json")
        .set("Authorization", `Bearer ${props.accessToken}`)
        .send({ chat_history: [] });
      const latestHistory = await fetchChatHistoryFromBackend();
      setChatbotState((prev) => ({
        ...prev,
        messages: latestHistory,
      }));
      setChatbotInstanceKey((prev) => prev + 1);
    } catch (err) {
      console.error("Failed to reset chat history on backend", err);
    }
  };

  return (
    <Row>
      <Col xs={10}>
        <div className={`app-chatbot-container${expanded ? " expanded" : ""}`}>
          <div style={{ maxWidth: "100%", maxHeight: "100%" }}>
            {/* Chatbot loads chat history from backend and renders it on UI load */}
            {showBot && initialMessages === null && <div>Loading chat...</div>}
            {showBot && initialMessages !== null && (
              <Chatbot
                key={chatbotInstanceKey}
                config={{
                  ...config_chatbot,
                  initialMessages: initialMessages,
                }}
                actionProvider={ActionProvider}
                messageParser={MessageParser}
                saveMessages={saveMessages}
                messageHistory={chatMessagesToIMessages(chatbotState.messages)}
                placeholderText={"Type something..."}
                runInitialMessagesWithHistory={true}
              />
            )}

            <button
              className="app-chatbot-button"
              onClick={() => toggleBot((prev) => !prev)}
            >
              <ChatIcon />
            </button>
          </div>
        </div>
      </Col>
    </Row>
  );
};

export default ChatBotComponent;
