
async function getResult(){
    let result = await getAll();
    return result
}

async function doTask(){
    let data = await getResult();
    console.log(data.data)
    document.getElementById('name').innerHTML = data.data.person[0];
    document.getElementById('email').innerHTML = data.data.person[1];
    document.getElementById('contact').innerHTML = data.data.person[2];

    document.getElementById('owner').innerHTML = data.data.car[0];
    document.getElementById('number').innerHTML = data.data.car[1];
    document.getElementById('brand').innerHTML = data.data.car[2];
}

function getAll(){
    try {
        const response = axios.get(`http://127.0.0.1:8000/dashboard/stream/result`);
        const todoItems = response;
        console.log(`GET: Here's the list of todos`, todoItems);
    
        return todoItems;
      } catch (errors) {
        console.error(errors);
      }
}


