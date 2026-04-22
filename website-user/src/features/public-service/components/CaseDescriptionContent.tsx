const MAP_LINK = 'https://www.traffic.ntpc.gov.tw/home.jsp?id=e081eb8c5e64ce7e' as const

export function CaseDescriptionContent() {
  return (
    <div className="max-w-none text-sm text-foreground">
      <h2 className="text-lg font-semibold">網頁維護</h2>
      <p>新北市政府警察局交通警察大隊</p>

      <h2 className="mt-6 text-lg font-semibold">申請說明</h2>
      <p>無</p>

      <h2 className="mt-6 text-lg font-semibold">申請對象</h2>
      <p>民眾</p>

      <h2 className="mt-6 text-lg font-semibold">承辦資訊</h2>
      <ul className="list-none pl-0">
        <li>承辦單位：新北市政府警察局交通警察大隊</li>
        <li>地址：新北市中和區中正路1167號</li>
        <li>承辦人員：曾臆任</li>
        <li>聯絡電話：(02)22255999 # 4517</li>
        <li>傳真號碼：(02)22259997</li>
      </ul>

      <h2 className="mt-6 text-lg font-semibold">應備證件</h2>
      <p className="font-medium">申請人應自行檢附之文件：</p>
      <ol className="list-decimal pl-5">
        <li>大貨車臨時通行證申請書（民）表一。</li>
        <li>行車執照影本（拖車使用證），依行車執照應定檢日前有效（檢驗）日期內核准通行。</li>
        <li>工程合約書或訂購單。</li>
        <li>棄土場同意書暨棄土流向證明。</li>
        <li>其他（委託書）。</li>
        <li>行駛起、訖路線地圖。</li>
      </ol>

      <h2 className="mt-6 text-lg font-semibold">備註</h2>
      <ul className="list-disc pl-5">
        <li>每次申請時間以 6 個月為限；核准通行日期至行車執照指定檢驗日期止。（每日 7~9 時及 17~19 時為禁止通行時段）</li>
        <li>通行起訖時間未填寫者將自申請日核予 1 個月。</li>
      </ul>

      <h2 className="mt-6 text-lg font-semibold">系統代為查調，申請人免自行檢附之文件</h2>
      <p>無</p>

      <h2 className="mt-6 text-lg font-semibold">申請方式</h2>
      <ul className="list-disc pl-5">
        <li>臨櫃：親自送件，審核通過後，通知通行證申請人親領。</li>
        <li>郵寄：審核通過後，通行證申請人親領或採郵寄方式（申請人須附回郵信封）。</li>
        <li>線上：申請時，上傳相關文件表單。</li>
      </ul>

      <h2 className="mt-6 text-lg font-semibold">交付方式</h2>
      <p>審核通過後，通行證申請人親領或採郵寄方式（申請人須附回郵信封）。</p>

      <h2 className="mt-6 text-lg font-semibold">處理期限</h2>
      <p>6 天</p>

      <h2 className="mt-6 text-lg font-semibold">備註連結</h2>
      <p>
        <a className="text-primary underline-offset-4 hover:underline" href={MAP_LINK} target="_blank" rel="noreferrer">
          新北市大貨車行駛路線及禁行區域圖
        </a>
      </p>
    </div>
  )
}
