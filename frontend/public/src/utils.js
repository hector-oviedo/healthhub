function formatDate(dateString) {
    // Try to parse the date string
    const date = new Date(dateString);

    // Check if the date is valid
    if (!isNaN(date.getTime())) {
        // Extract day, month, year, hours, and minutes
        let day = date.getDate().toString().padStart(2, '0');
        let month = (date.getMonth() + 1).toString().padStart(2, '0'); // Months are 0-based
        let year = date.getFullYear().toString().substr(-2); // Last two digits of the year
        let hours = date.getHours().toString().padStart(2, '0');
        let minutes = date.getMinutes().toString().padStart(2, '0');

        // Format the date string
        return `${day}/${month}/${year} ${hours}:${minutes}`;
    } else {
        // Return the original string if it's not a valid date
        return dateString;
    }
}
function formatDateToService(date, time) {
    // Combine the date and time with a 'T' separator
    const dateTime = `${date}T${time}`;

    // Create a Date object from the combined string
    const dateObj = new Date(dateTime);

    // Format the date and time in "YYYY-MM-DD HH:MM" format
    const year = dateObj.getFullYear();
    const month = (dateObj.getMonth() + 1).toString().padStart(2, '0'); // Month is 0-indexed
    const day = dateObj.getDate().toString().padStart(2, '0');
    const hours = dateObj.getHours().toString().padStart(2, '0');
    const minutes = dateObj.getMinutes().toString().padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}`;
}