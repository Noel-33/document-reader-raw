import { useEffect, useMemo, useState } from "react";
import {
  Layout, Typography, Card, Upload, Button, Select, Input, Space, Tag, Divider, message
} from "antd";
import { UploadOutlined, SendOutlined, FileTextOutlined } from "@ant-design/icons";
import { ConfigProvider } from "antd";
import { theme } from "./theme";
import { fetchModels, uploadFiles, listDocs, previewDoc, chat } from "./api";
import type { DocItem } from "./api";

import PdfPreview from "./PdfPreview";

const { Header, Sider, Content } = Layout;
const { Title, Text } = Typography;

const HEADER_H = 64;

export default function App() {
  const [models, setModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [docs, setDocs] = useState<DocItem[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [selectedDocIdsForChat, setSelectedDocIdsForChat] = useState<string[]>([]);
  const [preview, setPreview] = useState<string>("");
  const [question, setQuestion] = useState<string>("");
  const [chatLog, setChatLog] = useState<Array<{ role: "user" | "assistant"; text: string }>>([]);
  const [loadingChat, setLoadingChat] = useState(false);

  const selectedDoc = useMemo(() => docs.find(d => d.doc_id === selectedDocId), [docs, selectedDocId]);

  async function refreshDocs() {
    const d = await listDocs();
    setDocs(d);
    if (d.length && !selectedDocId) setSelectedDocId(d[0].doc_id);
  }

  useEffect(() => {
    (async () => {
      const m = await fetchModels();
      setModels(m);
      setSelectedModel(m[0] || "");
      await refreshDocs();
    })();

  }, []);

  useEffect(() => {
    (async () => {
      if (!selectedDocId) return;
      const p = await previewDoc(selectedDocId);
      setPreview(p.preview || "");
    })();
  }, [selectedDocId]);

  async function onUpload(fileList: File[]) {
    try {
      await uploadFiles(fileList);
      message.success("Uploaded and indexed in memory.");
      await refreshDocs();
    } catch (e: any) {
      message.error(e?.message || "Upload failed");
    }
  }

  async function onAsk() {
    if (!question.trim()) return;
    if (!selectedModel) return message.warning("Select a model first.");
    if (!selectedDocIdsForChat.length) return message.warning("Select at least one document for chat.");

    const q = question.trim();
    setQuestion("");
    setChatLog(prev => [...prev, { role: "user", text: q }]);
    setLoadingChat(true);

    try {
      const res = await chat(q, selectedModel, selectedDocIdsForChat);
      setChatLog(prev => [...prev, { role: "assistant", text: res.answer }]);
    }
    catch (e: any) {
  const detail = e?.response?.data?.detail;
  message.error(detail || e?.message || "Chat failed");
    }
    finally {
      setLoadingChat(false);
    }
  }

  return (
    <ConfigProvider theme={theme}>
      <Layout style={{ minHeight: "100vh" }}>
        <Header
  style={{
    height: HEADER_H,
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "0 16px",
    borderBottom: "1px solid #e6eaf2",
    background: "#fff",
  }}
>
  <Title level={3} style={{ margin: 0, color: "#0b1220" }}>
    Document Reader
  </Title>

  <Space>
    <Text style={{ color: "#0b1220" }}>LLM Model</Text>
    <Select
      style={{ width: 280 }}
      value={selectedModel}
      onChange={setSelectedModel}
      options={models.map((m) => ({ value: m, label: m }))}
    />
  </Space>
</Header>


        <Layout style={{ height: `calc(100vh - ${HEADER_H}px)` }}>
          <Sider width={360} style={{ padding: 16, overflow: "auto" }}>
            <Card title="Upload documents">
              <Upload
                multiple
                beforeUpload={(file, fileList) => {
                  const files = fileList.map(f => f as any as File);
                  onUpload(files);
                  return false;
                }}
                showUploadList={false}
              >
                <Button icon={<UploadOutlined />}>Select files</Button>
              </Upload>

              <Divider />

              <Text style={{ color: "#9FB0C0" }}>Stored in memory (resets when backend restarts)</Text>

              <Divider />

              <Card size="small" title="Documents">
                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  {docs.map((d) => (
                    <div
                      key={d.doc_id}
                      onClick={() => setSelectedDocId(d.doc_id)}
                      style={{
                        cursor: "pointer",
                        padding: 10,
                        borderRadius: 10,
                        border: d.doc_id === selectedDocId ? "1px solid #1677ff" : "1px solid #e6eaf2",
                        background: d.doc_id === selectedDocId ? "#eef5ff" : "#fff",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        gap: 10,
                      }}
                    >
                      <Space>
                        <FileTextOutlined />
                        <span style={{ color: "#0b1220" }}>
                          {d.filename}
                        </span>
                      </Space>
                      <Tag color="blue">{d.filetype.toUpperCase()}</Tag>

                    </div>
                  ))}
                </div>
              </Card>

              <Divider />

              <Card size="small" title="Use for chat (multi-select)">
                <Select
                  mode="multiple"
                  style={{ width: "100%" }}
                  placeholder="Select documents to include in retrieval"
                  value={selectedDocIdsForChat}
                  onChange={setSelectedDocIdsForChat}
                  options={docs.map(d => ({ value: d.doc_id, label: d.filename }))}
                />
              </Card>
            </Card>
          </Sider>

          <Content style={{ padding: 16, overflow: "hidden", height: "100%" }}>
            <div style={{ display: "flex", gap: 16, height: "100%", minHeight: 0 }}>
              {/* Chat */}
              <Card
  title="Chat"
  style={{
    flex: 1,
    height: "100%",
    minHeight: 0,
    display: "flex",
    flexDirection: "column",
  }}
  styles={{
    body: {
      flex: 1,
      minHeight: 0,
      overflow: "hidden",
      display: "flex",
      flexDirection: "column",
    },
  }}
>
  {/* Scrollable messages */}
  <div style={{ flex: 1, overflowY: "auto", paddingRight: 8, minHeight: 0 }}>
    {chatLog.length === 0 ? (
      <Text style={{ color: "#9FB0C0" }}>
        Upload documents, select docs for chat, then ask a question.
      </Text>
    ) : (
      chatLog.map((m, idx) => (
        <div key={idx} style={{ marginBottom: 12 }}>
          <div
  style={{
    maxWidth: "90%",
    marginLeft: m.role === "user" ? "auto" : 0,
    padding: "10px 12px",
    borderRadius: 12,
    background: m.role === "user" ? "#1677ff" : "#ffffff",
    color: m.role === "user" ? "#ffffff" : "#0b1220",
    border: m.role === "user" ? "1px solid #1677ff" : "1px solid #e6eaf2",
    boxShadow: "0 1px 2px rgba(16,24,40,0.06)",
    whiteSpace: "pre-wrap",
  }}
>
  {m.text}
</div>
        </div>
      ))
    )}
  </div>

  <Divider style={{ margin: "12px 0" }} />

  {/* Bigger typing area */}
  <div style={{ display: "flex", gap: 10, alignItems: "flex-end" }}>
    <Input.TextArea
      value={question}
      onChange={(e) => setQuestion(e.target.value)}
      placeholder="Ask a question..."
      autoSize={{ minRows: 3, maxRows: 6 }}
      style={{ resize: "none" }}
    />
    <Button type="primary" onClick={onAsk} loading={loadingChat} style={{ height: "100%" }}>
      Send
    </Button>
  </div>
</Card>




 {/* Preview */}
              <Card
  title={selectedDoc ? `Preview: ${selectedDoc.filename}` : "Preview"}
  style={{ width: 620, height: "100%", display: "flex", flexDirection: "column" }}
  styles={{
    body: { flex: 1, overflow: "auto", minHeight: 0 },
  }}
>


<div style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>
  {selectedDoc?.filetype === "pdf" ? (
    <div style={{ flex: 1, minHeight: 0 }}>
      <PdfPreview url={`http://localhost:8000/documents/${selectedDoc.doc_id}/file`} />
    </div>
  ) : (
    <div style={{ flex: 1, minHeight: 0, overflow: "auto", whiteSpace: "pre-wrap", color: "#0b1220" }}>
      {preview || "Select a document to preview."}
    </div>
  )}
</div>
</Card>
            </div>
          </Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
}
