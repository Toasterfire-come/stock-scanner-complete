/**
 * WebSocket client with automatic reconnection
 * Handles network interruptions gracefully
 *
 * Usage:
 * import ReconnectingWebSocket from './utils/websocket';
 *
 * const ws = new ReconnectingWebSocket('ws://localhost:8000/ws/stocks/', {
 *   maxReconnectAttempts: 10,
 *   reconnectInterval: 1000,
 *   debug: true
 * });
 *
 * ws.addEventListener('open', () => console.log('Connected'));
 * ws.addEventListener('message', (event) => console.log('Received:', event.data));
 * ws.send({type: 'subscribe', symbols: ['AAPL', 'GOOGL']});
 */
class ReconnectingWebSocket {
  constructor(url, options = {}) {
    this.url = url;
    this.options = {
      maxReconnectAttempts: options.maxReconnectAttempts || 10,
      reconnectInterval: options.reconnectInterval || 1000,
      reconnectDecay: options.reconnectDecay || 1.5,
      maxReconnectInterval: options.maxReconnectInterval || 30000,
      debug: options.debug || false,
      ...options
    };

    this.reconnectAttempts = 0;
    this.currentReconnectInterval = this.options.reconnectInterval;
    this.ws = null;
    this.forcedClose = false;
    this.listeners = {
      open: [],
      message: [],
      error: [],
      close: []
    };

    this.connect();
  }

  connect() {
    if (this.forcedClose) return;

    if (this.options.debug) {
      console.log(`[WebSocket] Connecting to ${this.url}...`);
    }

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = (event) => {
        if (this.options.debug) {
          console.log('[WebSocket] Connected');
        }
        this.reconnectAttempts = 0;
        this.currentReconnectInterval = this.options.reconnectInterval;
        this.listeners.open.forEach(fn => fn(event));
      };

      this.ws.onmessage = (event) => {
        this.listeners.message.forEach(fn => fn(event));
      };

      this.ws.onerror = (event) => {
        if (this.options.debug) {
          console.error('[WebSocket] Error:', event);
        }
        this.listeners.error.forEach(fn => fn(event));
      };

      this.ws.onclose = (event) => {
        if (this.options.debug) {
          console.log('[WebSocket] Closed. Code:', event.code);
        }

        this.listeners.close.forEach(fn => fn(event));

        // Don't reconnect if closed normally or forcedClose is true
        if (!this.forcedClose && event.code !== 1000) {
          this.reconnect();
        }
      };

    } catch (error) {
      console.error('[WebSocket] Connection error:', error);
      this.reconnect();
    }
  }

  reconnect() {
    if (this.forcedClose) return;

    if (this.reconnectAttempts >= this.options.maxReconnectAttempts) {
      console.error('[WebSocket] Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;

    if (this.options.debug) {
      console.log(
        `[WebSocket] Reconnecting in ${this.currentReconnectInterval}ms ` +
        `(attempt ${this.reconnectAttempts}/${this.options.maxReconnectAttempts})`
      );
    }

    setTimeout(() => {
      this.connect();
      this.currentReconnectInterval = Math.min(
        this.currentReconnectInterval * this.options.reconnectDecay,
        this.options.maxReconnectInterval
      );
    }, this.currentReconnectInterval);
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(typeof data === 'string' ? data : JSON.stringify(data));
    } else {
      console.warn('[WebSocket] Cannot send - connection not open');
    }
  }

  close() {
    this.forcedClose = true;
    if (this.ws) {
      this.ws.close();
    }
  }

  addEventListener(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event].push(callback);
    }
  }

  removeEventListener(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(fn => fn !== callback);
    }
  }

  get readyState() {
    return this.ws ? this.ws.readyState : WebSocket.CLOSED;
  }
}

export default ReconnectingWebSocket;
