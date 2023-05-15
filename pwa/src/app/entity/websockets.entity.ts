export enum WSConnection {
  WS_URL = 'ws://127.0.0.1:44331/ws',
  WS_PORT = 44331,
  WS_HOST = '127.0.0.1',
  RECONNECT_START = 2000,
}

export enum WSCommand {
  LOGIN = 'login',
  REPORT = 'report',
  REPORT_ID = 'report_id',
  TASKS = 'tasks',
  TASK = 'task',
}

export enum WSType {
  REQUEST = 'request',
  RESPONSE = 'response',
  PING = 'ping',
  PONG = 'pong',
  LOGIN = 'login',
}

export enum WSLoading {
  BLOCKING_ON = 'blocking_on',
  BLOCKING_OFF = 'blocking_off',
  MESSAGE_OFF = 'message_off',
  MESSAGE_ON = 'message_on',
}

export interface PayloadData {
  result: any;
}

export interface Payload {
  cmd: WSCommand;
  data?: PayloadData;
}

export interface WSRequest {
  ztype: WSType;
  id: string;
  client: string;
  data?: Payload;
}

export interface WSResponse {
  ztype: WSType;
  id: string;
  error?: string;
  data: Payload;
  client?: string;
}

export interface WSPing {
  ztype: WSType;
  id: string;
  client: string;
}

export interface WSPong {
  ztype: WSType;
  id: string;
}
