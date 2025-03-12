import {
  Container,
  EmptyState,
  Flex,
  Heading,
  Table,
  VStack,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { FiSearch } from "react-icons/fi"
import { z } from "zod"

import { WorkOrdersService } from "@/client"
import PendingWorkOrders from "@/components/Pending/PendingWorkOrders"
import { DetailsWorkOrders } from "../../components/WorkOrders/DetailsWorkOrders"
import {
  PaginationItems,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "@/components/ui/pagination.tsx"

const itemsSearchSchema = z.object({
  page: z.number().catch(1),
})

const PER_PAGE = 10

function getWorkOrdersQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      WorkOrdersService.readWorkOrders({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["items", { page }],
  }
}

export const Route = createFileRoute("/_layout/workorders")({
  component: WorkOrders,
  validateSearch: (search) => itemsSearchSchema.parse(search),
})

function WorkOrdensTable() {
  const navigate = useNavigate({ from: Route.fullPath })
  const { page } = Route.useSearch()

  const { data, isLoading, isPlaceholderData } = useQuery({
    ...getWorkOrdersQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const setPage = (page: number) =>
    navigate({
      search: (prev: { [key: string]: string }) => ({ ...prev, page }),
    })
  
  const items = data?.data.slice(0, PER_PAGE) ?? []
  const count = data?.count ?? 0

  if (isLoading) {
    return <PendingWorkOrders />
  }

  if (items.length === 0) {
    return (
      <EmptyState.Root>
        <EmptyState.Content>
          <EmptyState.Indicator>
            <FiSearch />
          </EmptyState.Indicator>
          <VStack textAlign="center">
            <EmptyState.Title>Usted no tiene órdenes de trabajo asignadas</EmptyState.Title>
          </VStack>
        </EmptyState.Content>
      </EmptyState.Root>
    )
  }

  return (
    <>
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
          {items?.map((item) => (
            <Table.Row key={item.workorder_id} opacity={isPlaceholderData ? 0.5 : 1}>
              <Table.Cell truncate maxW="sm">
                {item.name}
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {item.product}
              </Table.Cell>
              <Table.Cell truncate maxW="30%">
                {item.qty_remaining}
              </Table.Cell>
              <Table.Cell truncate maxW="30%">
                {item.state}
              </Table.Cell>
              <Table.Cell>
                <DetailsWorkOrders item={item} />
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>
      <Flex justifyContent="flex-end" mt={4}>
        <PaginationRoot
          count={count}
          pageSize={PER_PAGE}
          onPageChange={({ page }) => setPage(page)}
        >
          <Flex>
            <PaginationPrevTrigger />
            <PaginationItems />
            <PaginationNextTrigger />
          </Flex>
        </PaginationRoot>
      </Flex>
    </>
  )
}

function WorkOrders() {
  return (
    <Container maxW="full">
      <Heading size="lg" pt={12}>
        Órdenes de trabajo
      </Heading>
      <WorkOrdensTable />
    </Container>
  )
}
