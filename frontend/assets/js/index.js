import setTime from "./setTime.js";
let data;
const stockData = [];
const startDate = document.querySelector('[aria-label="start date"]');
const endDate = document.querySelector('[aria-label="end date"]');
const strategy = document.querySelector("#invest_strategy");
const form = document.querySelector(".card-body");
const symbol = document.querySelector("#symbol");
const investShortTerm = document.querySelector("#invest_short_term");
const investLongTerm = document.querySelector("#invest_long_term");
const type = document.querySelector("#transaction_type");

window.addEventListener("DOMContentLoaded", async () => {
  // const response = await fetch("https://api.fastrade.store/stocklist/");
  const response = await fetch("http://192.168.10.85:3000/stocklist/");
  data = await response.json();
  const stocklist = document.querySelector("#stocklist");
  data.stock_list.forEach((item) => {
    const option = document.createElement("option");
    option.value = `${item.symbol} ${item.name}`;
    stocklist.appendChild(option);
    stockData.push(option.value);
  });
});

setTime(startDate, endDate);

// 依據進場策略顯示不同參數;
strategy.addEventListener("change", (e) => {
  if (e.target.value === "MA") {
    investShortTerm.addEventListener("input", handleInputChange, true);
    investLongTerm.addEventListener("input", handleInputChange, true);
    investShortTerm.value = 5;
    investLongTerm.value = 20;
    investLongTerm.min = 10;
    investShortTerm.previousElementSibling.textContent = "短期均線參數";
    investLongTerm.previousElementSibling.textContent = "長期均線參數";
    investShortTerm.parentElement.parentElement.classList.replace(
      "col-md-4",
      "col-md-6"
    );
    investLongTerm.parentElement.parentElement.classList.replace(
      "col-md-4",
      "col-md-6"
    );
    if (document.querySelector("#dif")) {
      document.querySelector("#dif").parentElement.parentElement.remove();
    }
  } else if (e.target.value === "MACD" && !document.querySelector("#dif")) {
    investShortTerm.addEventListener("input", handleInputChange, true);
    investLongTerm.addEventListener("input", handleInputChange, true);
    investShortTerm.previousElementSibling.textContent = "短期均線參數";
    investLongTerm.previousElementSibling.textContent = "長期均線參數";
    investShortTerm.value = 12;
    investLongTerm.value = 26;
    investLongTerm.min = 10;
    investShortTerm.parentElement.parentElement.classList.replace(
      "col-md-6",
      "col-md-4"
    );
    investLongTerm.parentElement.parentElement.classList.replace(
      "col-md-6",
      "col-md-4"
    );
    const dif = `
                <div class="col-md-4">
                  <div class="input-group mb-3">
                    <label class="input-group-text" for="dif"
                      >DIF移動平均參數</label
                    >
                    <input
                      type="number"
                      id="dif"
                      class="form-control"
                      min="5"
                      value="9"
                      required
                    />
                  </div>
                </div>`;
    const element = document.querySelector(
      ".col-md-12.d-grid.justify-content-center"
    );
    element.insertAdjacentHTML("beforebegin", dif);
  } else if (e.target.value === "KD") {
    investShortTerm.removeEventListener("input", handleInputChange, true);
    investLongTerm.removeEventListener("input", handleInputChange, true);
    investShortTerm.previousElementSibling.textContent = "RSV參數";
    investLongTerm.previousElementSibling.textContent = "均線參數";
    investShortTerm.value = 9;
    investLongTerm.value = 3;
    investLongTerm.min = 3;
    investShortTerm.parentElement.parentElement.classList.replace(
      "col-md-4",
      "col-md-6"
    );
    investLongTerm.parentElement.parentElement.classList.replace(
      "col-md-4",
      "col-md-6"
    );
    if (document.querySelector("#dif")) {
      document.querySelector("#dif").parentElement.parentElement.remove();
    }
  }
});

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

// 驗證天期參數函式
function handleInputChange(event) {
  if (parseInt(investShortTerm.value) >= parseInt(investLongTerm.value)) {
    event.target.setCustomValidity("短天期參數必須小於長天期參數");
  } else {
    investShortTerm.setCustomValidity("");
    investLongTerm.setCustomValidity("");
  }
}

// 進場短天期參數驗證
investShortTerm.addEventListener("input", handleInputChange, true);

// 進場長天期參數驗證
investLongTerm.addEventListener("input", handleInputChange, true);

// 送出表單
form.addEventListener("submit", (event) => {
  event.preventDefault();
  const isValid = form.checkValidity();
  if (isValid) {
    const loading = document.querySelector("#loading");
    const loadingBg = document.querySelector("#loading-bg");
    const symbolNum = symbol.value.match(/\d+/)[0];
    const investAmount = parseInt(
      document.querySelector("#initial_amount").value
    );
    const shortTerm = parseInt(investShortTerm.value);
    const longTerm = parseInt(investLongTerm.value);
    async function backTest() {
      let url;
      loading.classList.remove("d-none");
      loadingBg.classList.remove("d-none");
      if (strategy.value === "MA") {
        // url = `https://api.fastrade.store/strategy/MA?transaction_type=${type.value}&short_term_ma=${shortTerm}&long_term_ma=${longTerm}&initial_capital=${investAmount}&start_date=${startDate.value}&end_date=${endDate.value}&symbol=${symbolNum}`;
        url = `http://192.168.10.85:3000/strategy/MA?transaction_type=${type.value}&short_term_ma=${shortTerm}&long_term_ma=${longTerm}&initial_capital=${investAmount}&start_date=${startDate.value}&end_date=${endDate.value}&symbol=${symbolNum}`;
      } else if (strategy.value === "KD") {
        // url = `https://api.fastrade.store/strategy/KD?transaction_type=${type.value}&recent_days=${shortTerm}&k_d_argument=${longTerm}&initial_capital=${investAmount}&start_date=${startDate.value}&end_date=${endDate.value}&symbol=${symbolNum}`;
        url = `http://192.168.10.85:3000/strategy/KD?transaction_type=${type.value}&recent_days=${shortTerm}&k_d_argument=${longTerm}&initial_capital=${investAmount}&start_date=${startDate.value}&end_date=${endDate.value}&symbol=${symbolNum}`;
      } else if (strategy.value === "MACD") {
        const dif = parseInt(document.querySelector("#dif").value);
        // url = `https://api.fastrade.store/strategy/MACD?transaction_type=${type.value}&short_term_macd=${shortTerm}&long_term_macd=${longTerm}&signal_dif=${dif}&initial_capital=${investAmount}&start_date=${startDate.value}&end_date=${endDate.value}&symbol=${symbolNum}`;
        url = `http://192.168.10.85:3000/strategy/MACD?transaction_type=${type.value}&short_term_macd=${shortTerm}&long_term_macd=${longTerm}&signal_dif=${dif}&initial_capital=${investAmount}&start_date=${startDate.value}&end_date=${endDate.value}&symbol=${symbolNum}`;
      }
      try {
        const response = await fetch(url);
        const backtestingResult = await response.json();
        const result = backtestingResult.backtesting_result;
        const num = Math.floor(Math.random() * 1000);
        const tableHtml = `
            <div class="card shadow-sm mt-3 mb-3">
              <div class="card-header d-flex justify-content-between">
                <div class="form-check form-switch">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="tableSwitch"
                    data-bs-toggle="collapse"
                    data-bs-target="#tableContent${num}"
                    aria-checked="false"
                  />
                  <label class="form-check-label" for="tableSwitch">詳細資料</label>
                </div>
                <button type="button" class="btn-close" aria-label="Close"></button>
              </div>
              <div class="table-responsive">
                <table class="table mb-0 table-secondary">
                  <thead>
                    <tr>
                      <th scope="col" class="text-center">股票代號</th>
                      <th scope="col" class="text-center">交易期間</th>
                      <th scope="col" class="text-center">淨損益</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <th scope="row" class="text-center bg-white">${symbol.value}</th>
                      <th scope="row" class="text-center bg-white">${startDate.value} ~ ${endDate.value}</th>
                      <th scope="row" class="text-center bg-white text-danger">${result.total_profit}</th>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div class="table-responsive collapse" id="tableContent${num}">
                <table class="table table-secondary">
                  <thead>
                    <tr>
                      <th scope="col" class="text-center">執行天數</th>
                      <th scope="col" class="text-center">交易次數</th>
                      <th scope="col" class="text-center">獲利次數</th>
                      <th scope="col" class="text-center">虧損次數</th>
                      <th scope="col" class="text-center">勝率</th>
                      <th scope="col" class="text-center">賺賠比</th>
                      <th scope="col" class="text-center">獲利因子</th>
                      <th scope="col" class="text-center">報酬率</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <th scope="row" class="text-center bg-white">${result.total_days}</th>
                      <th scope="row" class="text-center bg-white">${result.total_trades}</th>
                      <th scope="row" class="text-center bg-white">${result.num_wins}</th>
                      <th scope="row" class="text-center bg-white">${result.num_losses}</th>
                      <th scope="row" class="text-center bg-white">${result.win_rate}</th>
                      <th scope="row" class="text-center bg-white">${result.average_risk_reward_ratio}</th>
                      <th scope="row" class="text-center bg-white">${result.profit_factor}</th>
                      <th scope="row" class="text-center bg-white">${result.roi}</th>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          `;
        const element = document.querySelector(".row");
        element.insertAdjacentHTML("afterend", tableHtml);
        const close = document.querySelector(".btn-close");
        close.addEventListener("click", (e) => {
          e.target.parentElement.parentElement.remove();
        });
      } catch (e) {
        const tableHtml = `
            <div class="card shadow-sm mt-3 mb-3">
              <div class="card-header d-flex justify-content-end">
                <button type="button" class="btn-close" aria-label="Close"></button>
              </div>
              <div class="table-responsive">
                <table class="table">
                  <thead>
                    <tr>
                      <th scope="col" class="text-center">查無資料</th>
                    </tr>
                  </thead>
                </table>
              </div>
            </div>
          `;
        const element = document.querySelector(".row");
        element.insertAdjacentHTML("afterend", tableHtml);
        const close = document.querySelector(".btn-close");
        close.addEventListener("click", (e) => {
          e.target.parentElement.parentElement.remove();
        });
      } finally {
        // 隱藏 loading 畫面
        loading.classList.add("d-none");
        loadingBg.classList.add("d-none");
      }
    }
    backTest();
  }
});
