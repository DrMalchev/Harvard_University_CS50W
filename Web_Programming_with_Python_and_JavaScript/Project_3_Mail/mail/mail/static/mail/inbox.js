document.addEventListener('DOMContentLoaded', function () {
  let name;
  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => {
    name='inbox';
    load_mailbox(name); 
    });

  document.querySelector('#sent').addEventListener('click', () => {
    name='sent';
    load_mailbox(name);
  

});
  document.querySelector('#archived').addEventListener('click', () => {
    name='archive';
    load_mailbox('archive')
  });

  document.querySelector('#compose').addEventListener('click', () => {
    name='archive';
    compose_email();
  });

  // By default, load the inbox

  
  load_mailbox(name);
  


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

}

function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  
  
  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
    
}

function send_email() {
  //alert("Email sent successfully!");
  fetch("/emails", {
    method: "POST",
    body: JSON.stringify({
      recipients: document.querySelector('#compose-recipients').value,
      subject: document.querySelector('#compose-subject').value,
      body: document.querySelector('#compose-body').value
    })
  })
    .then(response => response.json())
    .then(result => {
      console.log("Email status ckeck: ", result);
      load_mailbox('sent');
      alert("Email sent successfully!");
      
      
    });
  
  //load_mailbox('sent');

  //alert("test check")
  //return false;
}