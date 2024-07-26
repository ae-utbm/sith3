import{join,basename}from"https://deno.land/std@0.108.0/path/mod.ts";import{errors}from"../util.js";const{INVALID:INVALID,GONE:GONE,MISMATCH:MISMATCH,MOD_ERR:MOD_ERR,SYNTAX:SYNTAX}=errors;async function fileFrom(t){const e=Deno.readFileSync(t),i=await Deno.stat(t);return new File([e],basename(t),{lastModified:Number(i.mtime)})}export class Sink{constructor(t,e){this.fileHandle=t,this.size=e,this.position=0}async abort(){await this.fileHandle.close()}async write(t){if("object"==typeof t)if("write"===t.type){if(Number.isInteger(t.position)&&t.position>=0&&(this.position=t.position),!("data"in t))throw await this.fileHandle.close(),new DOMException(...SYNTAX("write requires a data argument"));t=t.data}else{if("seek"===t.type){if(Number.isInteger(t.position)&&t.position>=0){if(this.size<t.position)throw new DOMException(...INVALID);return void(this.position=t.position)}throw await this.fileHandle.close(),new DOMException(...SYNTAX("seek requires a position argument"))}if("truncate"===t.type){if(Number.isInteger(t.size)&&t.size>=0)return await this.fileHandle.truncate(t.size),this.size=t.size,void(this.position>this.size&&(this.position=this.size));throw await this.fileHandle.close(),new DOMException(...SYNTAX("truncate requires a size argument"))}}if(t instanceof ArrayBuffer)t=new Uint8Array(t);else if("string"==typeof t)t=(new TextEncoder).encode(t);else if(t instanceof Blob){await this.fileHandle.seek(this.position,Deno.SeekMode.Start);for await(const e of t.stream()){const t=await this.fileHandle.write(e);this.position+=t,this.size+=t}return}await this.fileHandle.seek(this.position,Deno.SeekMode.Start);const e=await this.fileHandle.write(t);this.position+=e,this.size+=e}async close(){await this.fileHandle.close()}}export class FileHandle{#t;constructor(t,e){this.#t=t,this.name=e,this.kind="file"}async getFile(){return await Deno.stat(this.#t).catch((t=>{if("NotFound"===t.name)throw new DOMException(...GONE)})),fileFrom(this.#t)}async isSameEntry(t){return this.#t===this.#e.apply(t)}#e(){return this.#t}async createWritable(t){const e=await Deno.open(this.#t,{write:!0,truncate:!t.keepExistingData}).catch((t=>{if("NotFound"===t.name)throw new DOMException(...GONE);throw t})),{size:i}=await e.stat();return new Sink(e,i)}}export class FolderHandle{#t="";constructor(t,e=""){this.name=e,this.kind="directory",this.#t=join(t)}async isSameEntry(t){return this.#t===this.#e.apply(t)}#e(){return this.#t}async*entries(){const t=this.#t;try{for await(const e of Deno.readDir(t)){const{name:i}=e,n=join(t,i),o=await Deno.lstat(n);o.isFile?yield[i,new FileHandle(n,i)]:o.isDirectory&&(yield[i,new FolderHandle(n,i)])}}catch(t){throw"NotFound"===t.name?new DOMException(...GONE):t}}async getDirectoryHandle(t,e){const i=join(this.#t,t),n=await Deno.lstat(i).catch((t=>{if("NotFound"!==t.name)throw t})),o=n?.isDirectory;if(n&&o)return new FolderHandle(i,t);if(n&&!o)throw new DOMException(...MISMATCH);if(!e.create)throw new DOMException(...GONE);return await Deno.mkdir(i),new FolderHandle(i,t)}async getFileHandle(t,e){const i=join(this.#t,t),n=await Deno.lstat(i).catch((t=>{if("NotFound"!==t.name)throw t})),o=n?.isFile;if(n&&o)return new FileHandle(i,t);if(n&&!o)throw new DOMException(...MISMATCH);if(!e.create)throw new DOMException(...GONE);return(await Deno.open(i,{create:!0,write:!0})).close(),new FileHandle(i,t)}async queryPermission(){return"granted"}async removeEntry(t,e){const i=join(this.#t,t);(await Deno.lstat(i).catch((t=>{if("NotFound"===t.name)throw new DOMException(...GONE);throw t}))).isDirectory?e.recursive?await Deno.remove(i,{recursive:!0}).catch((t=>{if("ENOTEMPTY"===t.code)throw new DOMException(...MOD_ERR);throw t})):await Deno.remove(i).catch((()=>{throw new DOMException(...MOD_ERR)})):await Deno.remove(i)}}export default t=>new FolderHandle(join(Deno.cwd(),t));