const BASE = '/form-downloads' as const

export type FormDownloadItem = {
  group: 'procedure' | 'example'
  displayName: string
  format: 'pdf' | 'doc' | 'odt'
  storedFileName: string
  url: string
}

function item(
  g: 'procedure' | 'example',
  displayName: string,
  format: 'pdf' | 'doc' | 'odt',
  storedFileName: string,
): FormDownloadItem {
  return {
    group: g,
    displayName,
    format,
    storedFileName,
    url: `${BASE}/${encodeURIComponent(storedFileName)}`,
  }
}

/** 實體檔需置於 public/form-downloads/（檔名與 storedFileName 一致） */
export const FORM_DOWNLOAD_ITEMS: FormDownloadItem[] = [
  item('procedure', '申請大貨車臨時通行證流程圖', 'pdf', 'apply-hgv-temp-permit-flowchart.pdf'),
  item('procedure', '申請大貨車臨時通行證-作業流程說明', 'doc', 'apply-hgv-temp-permit-process.doc'),
  item('procedure', '（民）警交運07-(民)表一（3）', 'doc', 'form-min-table1-v3.doc'),
  item('procedure', '（民）警交運07-(民)表一（3）', 'odt', 'form-min-table1-v3.odt'),
  item('procedure', '（民）警交運07-(民)表一（3）', 'pdf', 'form-min-table1-v3.pdf'),
  item('example', '（民）警交運07-(民)表一-參考範例', 'doc', 'form-min-table1-example.doc'),
  item('example', '（民）警交運07-(民)表一-參考範例', 'odt', 'form-min-table1-example.odt'),
]

export const FORM_DOWNLOAD_GROUP_LABEL: Record<FormDownloadItem['group'], string> = {
  procedure: '作業程序',
  example: '填寫範例',
}
