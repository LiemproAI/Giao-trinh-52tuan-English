export class LocalSpeech {
 private audio: HTMLAudioElement | null = null;
 private request: AbortController | null = null;
 private url = '';
 private sequence = 0;
 stop() {
  this.sequence++;
  this.request?.abort();
  this.request = null;
  this.audio?.pause();
  this.audio = null;
  if (this.url) URL.revokeObjectURL(this.url);
  this.url = '';
 }
 async speak(text: string, rate: number, notify: (message: string) => void) {
  this.stop();
  const sequence = this.sequence;
  const controller = new AbortController();
  this.request = controller;
  notify('Đang chuẩn bị giọng Hải Đăng…');
  try {
   const response = await fetch('/api/tts', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({text}), signal: controller.signal});
   if (!response.ok) {const error = await response.json() as {error?: string}; throw new Error(error.error || 'Không tạo được giọng đọc.');}
   const blob = await response.blob();
   if (sequence !== this.sequence) return;
   this.url = URL.createObjectURL(blob);
   const audio = new Audio(this.url);
   this.audio = audio;
   audio.playbackRate = rate;
   audio.onended = () => {if (sequence === this.sequence) this.stop();};
   audio.onerror = () => {if (sequence === this.sequence) {this.stop(); notify('Không phát được WAV giọng Hải Đăng.');}};
   await audio.play();
  } catch (error) {
   if (sequence === this.sequence && !controller.signal.aborted) {this.stop(); notify(error instanceof Error ? error.message : 'Không kết nối được VieNeu Studio.');}
  }
 }
}
