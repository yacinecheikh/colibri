let main = async () => {
  let result = await client.list_addresses()
  alert(result)
}
main()
