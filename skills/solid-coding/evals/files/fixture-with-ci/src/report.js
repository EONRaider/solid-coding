// Deliberate Law of Demeter violation for the solid-coding eval suite:
// reaches through three accessors instead of asking `order` directly.
function printCustomerCity(order) {
  console.log(order.getCustomer().getAddress().getCity().toUpperCase());
}

module.exports = { printCustomerCity };
