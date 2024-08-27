export const errors={INVALID:["seeking position failed.","InvalidStateError"],GONE:["A requested file or directory could not be found at the time an operation was processed.","NotFoundError"],MISMATCH:["The path supplied exists, but was not an entry of requested type.","TypeMismatchError"],MOD_ERR:["The object can not be modified in this way.","InvalidModificationError"],SYNTAX:e=>[`Failed to execute 'write' on 'UnderlyingSinkBase': Invalid params passed. ${e}`,"SyntaxError"],SECURITY:["It was determined that certain files are unsafe for access within a Web application, or that too many calls are being made on file resources.","SecurityError"],DISALLOWED:["The request is not allowed by the user agent or the platform in the current context.","NotAllowedError"]};export const config={writable:globalThis.WritableStream};export async function fromDataTransfer(e){console.warn("deprecated fromDataTransfer - use `dt.items[0].getAsFileSystemHandle()` instead");const[t,r,a]=await Promise.all([import("./adapters/memory.js"),import("./adapters/sandbox.js"),import("./FileSystemDirectoryHandle.js")]),n=new t.FolderHandle("",!1);return n._entries=e.map((e=>e.isFile?new r.FileHandle(e,!1):new r.FolderHandle(e,!1))),new a.FileSystemDirectoryHandle(n)}export async function getDirHandlesFromInput(e){const{FolderHandle:t,FileHandle:r}=await import("./adapters/memory.js"),{FileSystemDirectoryHandle:a}=await import("./FileSystemDirectoryHandle.js"),n=Array.from(e.files),i=n[0].webkitRelativePath.split("/",1)[0],o=new t(i,!1);return n.forEach((e=>{const a=e.webkitRelativePath.split("/");a.shift();const n=a.pop();a.reduce(((e,r)=>(e._entries[r]||(e._entries[r]=new t(r,!1)),e._entries[r])),o)._entries[n]=new r(e.name,e,!1)})),new a(o)}export async function getFileHandlesFromInput(e){const{FileHandle:t}=await import("./adapters/memory.js"),{FileSystemFileHandle:r}=await import("./FileSystemFileHandle.js");return Array.from(e.files).map((e=>new r(new t(e.name,e,!1))))}