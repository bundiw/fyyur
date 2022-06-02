window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};
document.querySelectorAll(".delete-venue").forEach((delete_clicked) => {
  delete_clicked.addEventListener("click", (e) => {
    id = e.target.dataset["id"];
    prompt_respo = confirm("Are you sure you want to delete the venue?");
    if (prompt_respo) {
      fetch(`/venues/${id}`, {
        method: "DELETE",
      })
        .then((data) => data.json())
        .then((data) => {
          alert(`Venue delete ${data.message}`);
          location.reload();
        });
    }
  });
});
