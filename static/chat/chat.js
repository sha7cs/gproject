let category = null;
let subcategory = null;
let questionIndex = 0;
let isWaitingForResponse = false; 
const messages = document.getElementById("messages");
const chatSection = document.getElementById("chat-section");
const subcategoryButtons = document.getElementById("subcategory-buttons");
const categoryTitle = document.getElementById('categoryTitle')
const subcategoryTitle = document.getElementById('subcategoryTitle')
// const typingIndicator = document.querySelector("#typing-indicator");


function getSubcategoriesForCategory(categoryId) {
    return subcategoriesjs.filter(subcategory => subcategory.category == categoryId);
}

function selectCategory(categoryId) {
    const category = categoriesjs.find(category => category.id == categoryId).category;
    const mainCatgoriesButtons = document.getElementById("category-buttons");
    const subcategoryButtons = document.getElementById("subcategory-buttons");
    subcategoryButtons.innerHTML = '';

    const filteredSubcategories = getSubcategoriesForCategory(categoryId);

    if (filteredSubcategories.length > 0) {
        filteredSubcategories.forEach(subcategory => {
            subcategoryButtons.innerHTML += `
                <button class="custom-card-button mx-1" onclick="selectSubcategory('${subcategory.id}','${category}')">
                    ${subcategory.subcategory}
                </button>`;
        });
    mainCatgoriesButtons.style.display = "none"; // hide the category buttons
    subcategoryButtons.style.display = "flex"; // Show the subcategory buttons
    categoryTitle.style.display = "none";
    subcategoryTitle.style.display = "flex";
    } 
}

function selectSubcategory(subcategoryId,category) {
    subcategory = subcategoriesjs.find(subcategory => subcategory.id == subcategoryId).subcategory;
    const template = messages.dataset.chatTemplate;

    const finalMessage = template
    .replace("{category}", category)
    .replace("{subcategory}", subcategory);
  
    messages.innerHTML += `<div class="message bot">${finalMessage}</div>`;
    if (isWaitingForResponse) return; // Prevent sending multiple requests
    isWaitingForResponse = true; // Block further requests

    subcategoryButtons.style.display = "none";
    subcategoryTitle.style.display = "none";
    chatSection.classList.add("active"); // Add the 'active' class to make it visible
   
    // إنشاء مؤشر الكتابة
    const typingIndicator = document.createElement("div");
    typingIndicator.id = "typing-indicator";
    typingIndicator.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
    typingIndicator.classList.add("message", "bot");
    messages.appendChild(typingIndicator);

    questionIndex = 0;
    // Trigger the backend interaction by submitting the first request
    fetch('/'+lang+'/promotions/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'subcategory': subcategory,
            'category': category, 
            'question': '', 
            'response': '', 
            'questionIndex': 0, 
        }),
    })
    .then(response => response.json())
    .then(data => {
        // إزالة مؤشر الكتابة
        const existingIndicator = document.getElementById("typing-indicator");
        if (existingIndicator) {
            existingIndicator.remove();
        }
        // Display the first question from the backend
        if (data.response) {
            messages.innerHTML += `<div class="message bot">${data.response}</div>`;
            questionIndex = data.questionIndex; // Ensure correct index update
        }
        questionIndex = data.questionIndex || 0; // Update the question index
        messages.scrollTop = messages.scrollHeight; // Scroll to the latest message
    })
    .catch(error => console.error("Fetch Error:", error)).finally(() => {
        typingIndicator.style.display = "none";
        isWaitingForResponse = false; // Re-enable sending after response is received
    });
    }

    // Event listener for submitting user input
    document.getElementById("messageForm").addEventListener("submit", function (event) {
        event.preventDefault();
    
        const input = document.getElementById("messageInput");
        const userResponse = input.value.trim();
        if (userResponse === "") return;
    
        const messages = document.getElementById("messages");
        const currentQuestionElement = messages.querySelector(".message.bot:last-child");
        const currentQuestion = currentQuestionElement ? currentQuestionElement.textContent.trim() : "";
    
        messages.innerHTML += `<div class="message user">${userResponse}</div>`;
        input.value = "";
        // إنشاء مؤشر الكتابة
        const typingIndicator = document.createElement("div");
        typingIndicator.id = "typing-indicator";
        typingIndicator.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
        typingIndicator.classList.add("message", "bot");
        messages.appendChild(typingIndicator);
    
        // Send user response to backend
        fetch('/'+lang+'/promotions/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'category': category, 
                'subcategory': subcategory,
                'question': currentQuestion, 
                'response': userResponse,  
                'questionIndex': questionIndex, 
            }),
        })
        .then((response) => response.json())
        .then((data) => {
            // إزالة مؤشر الكتابة
            const existingIndicator = document.getElementById("typing-indicator");
            if (existingIndicator) {
                existingIndicator.remove();
            }

            if (data.response) {
                if (data.response !== currentQuestion) {
                    messages.innerHTML += `<div class="message bot">${data.response}</div>`;
                }
            }
            questionIndex = (data.questionIndex !== undefined) ? data.questionIndex : questionIndex + 1;
            messages.scrollTop = messages.scrollHeight;
        })
        .catch((error) => console.error("Error:", error));
    });
