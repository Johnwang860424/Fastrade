export default function setTime(startDate, endDate) {
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
}
