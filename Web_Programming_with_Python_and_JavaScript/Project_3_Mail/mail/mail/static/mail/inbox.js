
document.addEventListener('DOMContentLoaded', function () {
  
  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox')); 
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click',  compose_email);
  
  // By default, load the inbox
  
  if(name == 'inbox')  {load_mailbox('inbox');}
  else {load_mailbox(name);}
  
  
});



function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  //fourth input field is the submit button
  document.getElementsByTagName("INPUT")[3].addEventListener('click', send_email);

  const elements = document.getElementsByClassName('mailboxDiv');
    while(elements.length > 0){
        elements[0].parentNode.removeChild(elements[0]);
    }

  return false;
}

function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  
  
  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  name=mailbox;

  const elements = document.getElementsByClassName('mailboxDiv');
    while(elements.length > 0){
        elements[0].parentNode.removeChild(elements[0]);
    }
  //get data from mailbox
  fetch(`/emails/${mailbox}`)
    .then(response => response.text())
    .then(text => { 
      console.log(JSON.parse(text));
      JSON.parse(text).forEach(element => {
        
        console.log(element);

        let myDiv = document.createElement('div');
        myDiv.className = "mailboxDiv";
        myDiv.innerHTML=`<span style="margin-right:40px; font-weight:bold;">${element.sender} </span> <span>${element.subject}</span>  <span style="float:right;">${element.timestamp}</span>` ;
        
        document.body.appendChild(myDiv);
        
        
        if (element.read===true){myDiv.style.cssText ='border:1px solid black; max-width: 1024px; ; padding: 10px 15px 10px 15px; margin-left: 5%; margin-right:10%;background: lightgrey';}
        else {myDiv.style.cssText ='border:1px solid black; max-width: 1024px; ; padding: 10px 15px 10px 15px; margin-left: 5%; margin-right:10%';}
      });
    })
    .catch(err => console.error(err));  



}

function send_email() {
  //alert("Email sent successfully!");
  fetch("/emails", {
    method: "POST",
    body: JSON.stringify({
      recipients: document.querySelector('#compose-recipients').value,
      subject: document.querySelector('#compose-subject').value,
      body: document.querySelector('#compose-body').value
    }),
    headers: {'Content-type': 'application/json; charset=UTF-8'}
  })
    .then(response => response.json())
    .then(result => {
      console.log("Email status ckeck: ", result);
      
      //alert("Email sent successfully!");
      //window.stop(); 
      
      
    })
    .catch(err => console.error(err));
      let name = 'sent';
      load_mailbox('sent');
      //alert("Email sent successfully!");
      
  
}