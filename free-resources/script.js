var rpsButton = document.getElementById("rpsMac")
rpsButton.addEventListener("click", function(){
  window.location.href = window.location.href + "rockpaperscissors"
})

function download(file, text) {
  // creating an invisible element
  let element = document.createElement('a');
  element.setAttribute('href',
      'data:text/plain;charset=utf-8, '
      + encodeURIComponent(text));
  element.setAttribute('download', file);
  document.body.appendChild(element);
  element.click();

  document.body.removeChild(element);
}

// Start file download.

document.getElementById("rpsLinux")
    .addEventListener("click", function () {
        let text =
            document.getElementById("text").value;
        let filename = "rps-linux";

        download(filename, text);
    }, false);
