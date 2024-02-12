// Dynamic Image Loading (Lazy Loading)
const images = document.querySelectorAll("img");
const options = { threshold: 0.2 };

const imageObserver = new IntersectionObserver((entries, imgObserver) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      let image = entry.target;
      image.src = image.dataset.src || image.src; // Prioritize dataset.src (for local images)
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

      // Image Display
      if (message.image_path) {
        let img = document.createElement("img");
        img.classList.add("lazy");
        img.src = message.image_path; // Image from local file
        img.alt = "Image from Slack";
        messageDiv.appendChild(img);
      }

      container.appendChild(messageDiv);
    });
  });

// Fetch and Render Conversation Data
fetch("conversation.json")
  .then((response) => response.json())
  .then((data) => {
    const container = document.getElementById("conversation-container");
    data.forEach((message) => {
      // ... (Create 'messageDiv', 'userSpan', 'timestampSpan', 'textP' - similar to  before) ...

      // Profile Picture
      if (message.profile_image_url) {
        let profileImg = document.createElement("img");
        profileImg.src = message.profile_image_url;
        profileImg.alt = "Profile picture of " + message.user; // Descriptive alt text
        profileImg.classList.add("profile-pic"); // Add a class for optional styling
        messageDiv.appendChild(profileImg);
      }

      // ... (Adding image if present - existing code) ...

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
