import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8000",
});

export type DocItem = { doc_id: string; filename: string; filetype: string };

export async function fetchModels(): Promise<string[]> {
  const r = await api.get("/models");
  return r.data.models;
}

export async function uploadFiles(files: File[]): Promise<DocItem[]> {
  const form = new FormData();
  files.forEach((f) => form.append("files", f));
  const r = await api.post("/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return r.data;
}

export async function listDocs(): Promise<DocItem[]> {
  const r = await api.get("/documents");
  return r.data;
}

export async function previewDoc(docId: string): Promise<{ preview: string; filename: string }> {
  const r = await api.get(`/documents/${docId}/preview`);
  return r.data;
}

export async function chat(question: string, model: string, docIds: string[]) {
  const r = await api.post("/chat", { question, model, doc_ids: docIds });
  return r.data as { answer: string; sources: Array<any> };
}
