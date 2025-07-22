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
import { APIService } from "../../constants/APIConstant";
import request from "superagent";

interface State {
  initializationRequired?: boolean;
  initializing?: boolean;
  modelSelection?: boolean;
  accessToken: string;
  chatHistory: ChatMessage[];
}

export interface ChatMessage {
  role: string;
  content: string;
  id: number;
  loading?: boolean;
  terminateLoading?: boolean;
}

interface ActionProvider {
  handleHelp: (initRequired: boolean) => void;
  handleInitialize: (initRequired: boolean) => void;
  handleResetContext: (accessToken: string) => void;
  handleInitialized: (
    message: string,
    accessToken: string,
    chatHistory: ChatMessage[],
  ) => void;
  handleNotInitialized: () => void;
  handleModelSelection: (initRequired: boolean) => void;
  handleModelConfirmation: (message: string, accessToken: string) => void;
  handleChat: (message: string, accessToken: string) => void;
}

class MessageParser {
  private actionProvider: ActionProvider;
  private state: State;

  constructor(actionProvider: ActionProvider, state: State) {
    this.actionProvider = actionProvider;
    this.state = state;
  }

  async initializationRequired(): Promise<[boolean, ChatMessage[]]> {
    const stateUrl = APIService.CHATBOT_SERVICE + "genai/state";
    let initRequired = false;
    let chatHistory: ChatMessage[] = [];
    // Wait for the response
    await request
      .get(stateUrl)
      .set("Accept", "application/json")
      .set("Content-Type", "application/json")
      .set("Authorization", `Bearer ${this.state.accessToken}`)
      .then((res) => {
        console.log("I response:", res.body);
        if (res.status === 200) {
          if (res.body?.initialized === "true") {
            initRequired = false;
            if (res.body?.chat_history) {
              chatHistory = res.body?.chat_history;
            }
          } else {
            initRequired = true;
          }
        }
      })
      .catch((err) => {
        console.log("Error prefetch: ", err);
      });

    console.log("Initialization required:", initRequired);
    return [initRequired, chatHistory];
  }

  async parse(message: string): Promise<void> {
    console.log("State:", this.state);
    console.log("Message:", message);
    const message_l = message.toLowerCase();
    if (this.state?.initializationRequired === undefined) {
      const [initRequired, chatHistory] = await this.initializationRequired();
      this.state.initializationRequired = initRequired;
      this.state.chatHistory = chatHistory;
      console.log("State check:", this.state);
    }
    if (message_l === "help") {
      const [initRequired, chatHistory] = await this.initializationRequired();
      this.state.initializationRequired = initRequired;
      this.state.chatHistory = chatHistory;
      console.log("State help:", this.state);
      return this.actionProvider.handleHelp(this.state.initializationRequired);
    } else if (message_l === "init" || message_l === "initialize") {
      const [initRequired, chatHistory] = await this.initializationRequired();
      this.state.initializationRequired = initRequired;
      this.state.chatHistory = chatHistory;
      console.log("State init:", this.state);
      return this.actionProvider.handleInitialize(
        this.state.initializationRequired,
      );
    } else if (message_l === "model" || message_l === "models") {
      const [initRequired, chatHistory] = await this.initializationRequired();
      this.state.initializationRequired = initRequired;
      this.state.chatHistory = chatHistory;
      console.log("State help:", this.state);
      return this.actionProvider.handleModelSelection(
        this.state.initializationRequired,
      );
    } else if (
      message_l === "clear" ||
      message_l === "reset" ||
      message_l === "restart"
    ) {
      return this.actionProvider.handleResetContext(this.state.accessToken);
    } else if (this.state.initializing) {
      return this.actionProvider.handleInitialized(
        message,
        this.state.accessToken,
        this.state.chatHistory,
      );
    } else if (this.state.initializationRequired) {
      return this.actionProvider.handleNotInitialized();
    } else if (this.state.modelSelection) {
      return this.actionProvider.handleModelConfirmation(
        message,
        this.state.accessToken,
      );
    }

    return this.actionProvider.handleChat(message, this.state.accessToken);
  }
}

export default MessageParser;
