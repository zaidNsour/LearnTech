// Assuming your course select element has the ID "courseSelect"
// and the unit select element has the ID "unitSelect"
const courseSelect = document.getElementById("courseSelect");
const unitSelect = document.getElementById("unitSelect");

function updateUnits() {
  const selectedCourseId = courseSelect.value;

  // Make an AJAX request to fetch units based on the selected course ID
  fetch(`/get_units?course_id=${selectedCourseId}`)
    .then(response => response.json())  // Parse the JSON response
    .then(data => {
      // Clear the existing options in the unit select element
      unitSelect.innerHTML = "";

      // Add an option for "Select Unit" (optional)
      const defaultOption = document.createElement("option");
      defaultOption.value = "";
      defaultOption.text = "Select Unit";
      unitSelect.appendChild(defaultOption);

      // Add options for each unit retrieved from the server
      data.forEach(unit => {
        const option = document.createElement("option");
        option.value = unit.id;  // Assuming unit has an ID property
        option.text = unit.title;  // Assuming unit has a title property
        unitSelect.appendChild(option);
      });
    })
    .catch(error => {
      console.error("Error fetching units:", error);
      // Handle errors appropriately (e.g., display an error message)
    });
}

// Attach an event listener to the course select element
courseSelect.addEventListener("change", updateUnits);

// Call updateUnits initially to populate the unit select on page load
// (Optional, if you want units pre-populated based on a selected course)
updateUnits();