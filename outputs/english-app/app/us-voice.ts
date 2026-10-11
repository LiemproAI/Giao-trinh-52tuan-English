type Voice = {name: string; lang: string};
export function chooseUSVoice<T extends Voice>(voices: T[], preferred = ''): T | null {
 const us = voices.filter(v => v.lang.toLowerCase().replace('_','-') === 'en-us');
 const chosen = us.find(v => v.name === preferred);
 if (chosen) return chosen;
 // Select only voices actually exposed by the browser.
 for (const name of ['Aria', 'Jenny', 'Guy', 'Google US English', 'Zira', 'David']) {
  const voice = us.find(v => v.name.toLowerCase().includes(name.toLowerCase()));
  if (voice) return voice;
 }
 return us[0] || null;
}
