import { useMemo, useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import { Button, Space } from "antd";


pdfjs.GlobalWorkerOptions.workerSrc =
  `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

export default function PdfPreview({ url }: { url: string }) {
  const [numPages, setNumPages] = useState(0);
  const [scale, setScale] = useState(1.25);

  const pages = useMemo(
    () => Array.from({ length: numPages }, (_, i) => i + 1),
    [numPages]
  );

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <Space style={{ marginBottom: 10 }}>
        <Button onClick={() => setScale((s) => Math.max(0.6, s - 0.15))}>-</Button>
        <Button onClick={() => setScale((s) => Math.min(2.5, s + 0.15))}>+</Button>
        <span>{Math.round(scale * 100)}%</span>
      </Space>

      <div style={{ flex: 1, overflow: "auto" }}>
        <Document
          file={url}
          onLoadSuccess={(p) => setNumPages(p.numPages)}
          onLoadError={(err) => console.error("PDF load error:", err)}
        >
          {pages.map((p) => (
            <div key={p} style={{ marginBottom: 12 }}>
              <Page pageNumber={p} scale={scale} />
            </div>
          ))}
        </Document>
      </div>
    </div>
  );
}
