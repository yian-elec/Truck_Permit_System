/** Opens URL in new tab / triggers download (same-origin or signed URLs). */
export async function downloadByUrl(url: string, filename?: string): Promise<void> {
  const a = document.createElement('a')
  a.href = url
  a.target = '_blank'
  a.rel = 'noopener noreferrer'
  if (filename) a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
}
