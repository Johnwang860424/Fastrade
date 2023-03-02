let data;
// const stocksymbol = [];
// const stockName = [];
const stockData = [];
const startDate = document.querySelector('[aria-label="start date"]');
const endDate = document.querySelector('[aria-label="end date"]');
const form = document.querySelector(".card-body");
const symbol = document.querySelector("#symbol");
const investShortTerm = document.querySelector("#invest_short_term");
const investLongTerm = document.querySelector("#invest_long_term");
const leaveShortTerm = document.querySelector("#invest_short_term");
const leaveLongTerm = document.querySelector("#invest_long_term");

window.addEventListener("DOMContentLoaded", async () => {
  const response = await fetch("https://api.fastrade.store/stock_list/");
  data = await response.json();
  const stocklist = document.querySelector("#stocklist");
  data.stock_list.forEach((item) => {
    const option = document.createElement("option");
    option.value = `${item.symbol} ${item.name}`;
    stocklist.appendChild(option);
    // stocksymbol.push(item.symbol);
    // stockName.push(item.name);
    stockData.push(option.value);
  });
});

const setTime = () => {
  const twTimeZone = {
    timeZone: "Asia/Taipei",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  };
  const now = new Date();
  const dateString = now
    .toLocaleDateString("zh-TW", twTimeZone)
    .split("/")
    .join("-");

  startDate.max = dateString;
  endDate.max = dateString;
};

setTime();

// 股票代號驗證
symbol.addEventListener("change", (e) => {
  if (!stockData.includes(symbol.value)) {
    e.target.setCustomValidity("請輸入正確的股票代號");
  }
});
symbol.addEventListener("input", (e) => {
  e.target.value = e.target.value.replace(/^[a-zA-Z]/, "");
  e.target.setCustomValidity("");
});

// 開始日期驗證
startDate.addEventListener("change", (e) => {
  let newDate = new Date(e.target.value);
  newDate.setDate(newDate.getDate() + 30);
  newDate = newDate.toISOString().substring(0, 10);
  if (endDate.value < newDate) {
    e.target.setCustomValidity("開始日期必須小於結束日期30天以上");
  } else {
    e.target.setCustomValidity("");
    endDate.setCustomValidity("");
  }
});

// 結束日期驗證
endDate.addEventListener("change", (e) => {
  let newDate = new Date(e.target.value);
  newDate.setDate(newDate.getDate() - 30);
  newDate = newDate.toISOString().substring(0, 10);
  if (newDate < startDate.value) {
    e.target.setCustomValidity("結束日期必須大於開始日期30天以上");
  } else {
    e.target.setCustomValidity("");
    startDate.setCustomValidity("");
  }
});

// 進場短天期參數驗證
investShortTerm.addEventListener("input", (e) => {
  if (parseInt(e.target.value) >= parseInt(investLongTerm.value)) {
    e.target.setCustomValidity("短天期參數必須小於長天期參數");
  } else {
    e.target.setCustomValidity("");
  }
});

// 進場長天期參數驗證
investLongTerm.addEventListener("input", (e) => {
  if (parseInt(investShortTerm.value) >= parseInt(e.target.value)) {
    investShortTerm.setCustomValidity("");
    e.target.setCustomValidity("長天期參數必須大於短天期參數");
  } else {
    e.target.setCustomValidity("");
  }
});

// 進場短天期參數驗證
leaveShortTerm.addEventListener("input", (e) => {
  if (parseInt(e.target.value) >= parseInt(leaveLongTerm.value)) {
    e.target.setCustomValidity("短天期參數必須小於長天期參數");
  } else {
    e.target.setCustomValidity("");
  }
});

// 進場長天期參數驗證
leaveLongTerm.addEventListener("input", (e) => {
  if (parseInt(leaveShortTerm.value) >= parseInt(e.target.value)) {
    leaveShortTerm.setCustomValidity("");
    e.target.setCustomValidity("長天期參數必須大於短天期參數");
  } else {
    e.target.setCustomValidity("");
  }
});

// 送出表單
form.addEventListener("submit", (event) => {
  event.preventDefault();
  const isValid = form.checkValidity();
  if (isValid) {
    form.reset();
    const tableHtml = `
    <table class="table">
      <thead>
        <tr>
          <th scope="col">#</th>
          <th scope="col">First</th>
          <th scope="col">Last</th>
          <th scope="col">Handle</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th scope="row">1</th>
          <td>Mark</td>
          <td>Otto</td>
          <td>@mdo</td>
        </tr>
        <tr>
          <th scope="row">2</th>
          <td>Jacob</td>
          <td>Thornton</td>
          <td>@fat</td>
        </tr>
        <tr>
          <th scope="row">3</th>
          <td colspan="2">Larry the Bird</td>
          <td>@twitter</td>
        </tr>
      </tbody>
    </table>
  `;

    const element = document.querySelector(".row");
    element.insertAdjacentHTML("afterend", tableHtml);
  } else {
    console.log(form.reportValidity());
  }
});
