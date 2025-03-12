import { Table } from "@chakra-ui/react"
import { SkeletonText } from "../ui/skeleton"

const PendingWorkOrders = () => (
  <Table.Root size={{ base: "sm", md: "md" }}>
    <Table.Header>
      <Table.Row>
        <Table.ColumnHeader w="sm">Operación</Table.ColumnHeader>
        <Table.ColumnHeader w="sm">Producto</Table.ColumnHeader>
        <Table.ColumnHeader w="sm">Cantidad a producir</Table.ColumnHeader>
        <Table.ColumnHeader w="sm">Estado</Table.ColumnHeader>
      </Table.Row>
    </Table.Header>
    <Table.Body>
      {[...Array(5)].map((_, index) => (
        <Table.Row key={index}>
          <Table.Cell>
            <SkeletonText noOfLines={1} />
          </Table.Cell>
          <Table.Cell>
            <SkeletonText noOfLines={1} />
          </Table.Cell>
          <Table.Cell>
            <SkeletonText noOfLines={1} />
          </Table.Cell>
          <Table.Cell>
            <SkeletonText noOfLines={1} />
          </Table.Cell>         
        </Table.Row>
      ))}
    </Table.Body>
  </Table.Root>
)

export default PendingWorkOrders
