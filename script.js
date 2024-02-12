// Dynamic Image Loading
const images = document.querySelectorAll("img");
const options = { threshold: 0.2 };

const imageObserver = new IntersectionObserver((entries, imgObserver) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      let image = entry.target;
      image.src = image.dataset.src;
      image.classList.add("loaded");
      imageObserver.unobserve(image);
    }
  });
}, options);

images.forEach((image) => {
  imageObserver.observe(image);
});

// Fetch and Render Conversation Data
fetch("conversation.json")
  .then((response) => response.json())
  .then((data) => {
    const container = document.getElementById("conversation-container");
    data.forEach((message) => {
      let messageDiv = document.createElement("div");
      messageDiv.classList.add("message");

      let userSpan = document.createElement("span");
      userSpan.classList.add("user");
      userSpan.textContent = message.user;
      messageDiv.appendChild(userSpan);

      let timestampSpan = document.createElement("span");
      timestampSpan.classList.add("timestamp");
      timestampSpan.textContent = message.timestamp;
      messageDiv.appendChild(timestampSpan);

      let textP = document.createElement("p");
      textP.textContent = message.text;
      messageDiv.appendChild(textP);

      if (message.image_url) {
        let img = document.createElement("img");
        img.classList.add("lazy");
        img.dataset.src = message.image_url;
        img.alt = "Image from Slack";
        messageDiv.appendChild(img);
      }

      container.appendChild(messageDiv);
    });
  });

// Search Functionality
const searchBox = document.getElementById("search-box");
const messages = document.querySelectorAll(".message");

searchBox.addEventListener("input", () => {
  const searchTerm = searchBox.value.toLowerCase();
  messages.forEach((message) => {
    const textContent = message.textContent.toLowerCase();
    message.style.display = textContent.includes(searchTerm) ? "block" : "none";
  });
});
