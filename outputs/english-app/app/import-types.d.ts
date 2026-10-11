declare module 'mammoth/mammoth.browser.js' {
 const mammoth: {extractRawText(options:{arrayBuffer:ArrayBuffer}):Promise<{value:string}>};
 export default mammoth;
}
