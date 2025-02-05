let category = null;
let subcategory = null;
let questionIndex = 0;

const messages = document.getElementById("messages");
const chatSection = document.getElementById("chat-section");
const subcategoryButtons = document.getElementById("subcategory-buttons");
const categoryTitle = document.getElementById('categoryTitle')
const subcategoryTitle = document.getElementById('subcategoryTitle')


function getSubcategoriesForCategory(categoryId) {
    return subcategoriesjs.filter(subcategory => subcategory.category == categoryId);
}

function selectCategory(categoryId) {
    
    const category = categoriesjs.find(category => category.id == categoryId).category
        // messages.innerHTML += `<div class="message bot">Please choose a subcategory.</div>`;
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
    } //else {
    //     messages.innerHTML += `<div class="message bot">No subcategries found</div>`;
    //     // messages.innerHTML += `<div class="message bot">${trans('NoSubcategories')}</div>`;
    // }

}

function selectSubcategory(subcategoryId,category) {
    // const form = document.getElementById("messageForm"); // Form containing the input field
    subcategory = subcategoriesjs.find(subcategory => subcategory.id == subcategoryId).subcategory;

    messages.innerHTML += `<div class="message bot">'You chose ${category} to chat about ${subcategory}. Please answer any given questions sincerly, so i can give you a good advice.</div>`;
   

    //

    subcategoryButtons.style.display = "none";
    subcategoryTitle.style.display = "none";
    chatSection.classList.add("active"); // Add the 'active' class to make it visible

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
            'questionIndex': questionIndex, 
        }),
    })
    .then(response => response.json())
    .then(data => {
        // Display the first question from the backend
        if (data.response) {
            messages.innerHTML += `<div class="message bot">${data.response}</div>`;
        }
        questionIndex = data.questionIndex || 0; // Update the question index
        messages.scrollTop = messages.scrollHeight; // Scroll to the latest message
    })
    .catch(error => console.error("Fetch Error:", error));
    }

    // Event listener for submitting user input
    document.getElementById("messageForm").addEventListener("submit", function (event) {
    event.preventDefault(); //يمنع رفرش الصفحة

    const input = document.getElementById("messageInput");
    const userResponse = input.value.trim();
    if (userResponse === "") return;

    const messages = document.getElementById("messages");
    const currentQuestionElement = messages.querySelector(".message.bot:last-child");
    const currentQuestion = currentQuestionElement ? currentQuestionElement.textContent : "";

    messages.innerHTML += `<div class="message user">${userResponse}</div>`;
    input.value = "";

    // Send the current question and user response to the backend
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
        if (data.response) {
        messages.innerHTML += `<div class="message bot">${data.response}</div>`;
        }
        messages.scrollTop = messages.scrollHeight; // Scroll to the latest message

        questionIndex = data.questionIndex || questionIndex;
    })
    .catch((error) => console.error("Error:", error));
});
