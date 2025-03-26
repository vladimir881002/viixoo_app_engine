import {
  Container,
  EmptyState,
  Flex,
  Heading,
  Table,
  VStack,
  Button,
  Group,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { FiSearch } from "react-icons/fi"
import { z } from "zod"

import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

import { type ApiError, type ChangeStateWorkOrder, WorkOrdersService } from "@/client"
import PendingWorkOrders from "@/components/Pending/PendingWorkOrders"
import { DetailsWorkOrders } from "../../components/WorkOrders/DetailsWorkOrders"
import { BlockWorkOrders } from "../../components/WorkOrders/BlockWorkOrders"
import { MenuContent, MenuRoot, MenuTrigger } from "../../components/ui/menu"
import { IconButton } from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"
import {
  PaginationItems,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "@/components/ui/pagination.tsx"
import { useElapsedTime } from '../../hooks/elapsedTime';
import type { WorkOrderPublic } from "../../client/types.gen"

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

interface WorkOrderProps {
  item: WorkOrderPublic
}

export const formatDuration = (duration: number): string => {
  if (duration == 0) return "00:00";

  const minutes = Math.floor(duration);
  const seconds = Math.round((duration % 1) * 60);
  return `${minutes}:${seconds}`;
};

export const TimeElapsedWorkOrder = ( { item }: WorkOrderProps) => {
  const activeTime = item.time_ids?.find(time => !time.date_end);

  const date_start = activeTime?.date_start;
  
  const baseElapsed = useElapsedTime(date_start || "");
  
  const addFixedTime = (timeString: string) => {
    if (!timeString) return "00:00";
    
    const [minutes, seconds] = timeString.split(":").map(Number);
    const totalSeconds = (minutes * 60 + seconds);
    
    const durationMinutes = Math.floor(item.duration);
    const durationSeconds = Math.round((item.duration % 1) * 60);

    if (!timeString) return "00:00";

    const itemTotalSeconds = (durationMinutes * 60) + durationSeconds;
    
    const newTotalSeconds = totalSeconds + itemTotalSeconds;
    
    const newMinutes = Math.floor(newTotalSeconds / 60);
    const newSeconds = newTotalSeconds % 60;

    return `${String(newMinutes).padStart(2, '0')}:${String(newSeconds).padStart(2, '0')}`;
  };

  if (!date_start) return <>00:00</>;

  return <>{addFixedTime(baseElapsed)}</>;
};

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
  const queryClient = useQueryClient()  
  const { showSuccessToast } = useCustomToast()
  const mutationStartWorkorder = useMutation({
    mutationFn: (data: ChangeStateWorkOrder) =>
      WorkOrdersService.startWorkorder({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Orden iniciada satisfactoriamente.")
      queryClient.invalidateQueries({ queryKey: ["items"] })
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
  })

  const onClickStartWorkorder = async (data: ChangeStateWorkOrder) => {
    mutationStartWorkorder.mutate(data)
  }

  const mutationPauseWorkorder = useMutation({
    mutationFn: (data: ChangeStateWorkOrder) =>
      WorkOrdersService.pauseWorkorder({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Orden pausada satisfactoriamente.")
      queryClient.invalidateQueries({ queryKey: ["items"] })
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
  })

  const onClickPauseWorkorder= async (data: ChangeStateWorkOrder) => {
    mutationPauseWorkorder.mutate(data)
  }

  const mutationFinishWorkorder = useMutation({
    mutationFn: (data: ChangeStateWorkOrder) =>
      WorkOrdersService.finishWorkorder({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Orden terminada satisfactoriamente.")
      queryClient.invalidateQueries({ queryKey: ["items"] })
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
  })

  const onClickFinishWorkorder= async (data: ChangeStateWorkOrder) => {
    mutationFinishWorkorder.mutate(data)
  }

  const mutationUnblockWorkorder = useMutation({
    mutationFn: (data: ChangeStateWorkOrder) =>
      WorkOrdersService.unblockWorkorder({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Orden desbloqueada satisfactoriamente.")
      queryClient.invalidateQueries({ queryKey: ["items"] })
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
  })

  const onClickUnblockWorkorder= async (data: ChangeStateWorkOrder) => {
    mutationUnblockWorkorder.mutate(data)
  }

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
      <Table.Root size={{ base: "sm", md: "md" }} >
        <Table.Header>
          <Table.Row>
          <Table.ColumnHeader w="sm" fontWeight="bold">Operación</Table.ColumnHeader>
          <Table.ColumnHeader w="sm" fontWeight="bold">Producto</Table.ColumnHeader>
          <Table.ColumnHeader w="sm" fontWeight="bold">Cantidad a producir</Table.ColumnHeader>
          <Table.ColumnHeader w="sm" fontWeight="bold">Duración real</Table.ColumnHeader>
          <Table.ColumnHeader w="sm" fontWeight="bold">Estado</Table.ColumnHeader>
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
                {(item.is_user_working)?<TimeElapsedWorkOrder item={item}/>:formatDuration(item.duration)}
              </Table.Cell>
              <Table.Cell truncate maxW="30%">
                {item.state}
              </Table.Cell>
              <Table.Cell>
                <DetailsWorkOrders item={item} />
              </Table.Cell>
              <Table.Cell>
                <Group>
                <Button size="xs" onClick={() => onClickStartWorkorder({'workorder_id': item.workorder_id})} colorPalette="green" display={
                  ['done', 'cancel'].includes(item.state_value) || ['draft', 'done', 'cancel'].includes(item.production_state) || item.working_state == 'blocked' || item.is_user_working? 'none' : 'flex'
                }>Iniciar</Button>
                <Button size="xs" onClick={() => onClickFinishWorkorder({'workorder_id': item.workorder_id})} colorPalette="green" display={
                  ['draft', 'done'].includes(item.production_state) || item.working_state == 'blocked' || !item.is_user_working || (item.quality_state != "" && item.quality_state != "none")
                    || ['register_consumed_materials', 'register_byproducts', 'instructions'].includes(item.test_type)? 'none' : 'flex'
                }>Listo</Button>
                </Group>
              </Table.Cell>
              <Table.Cell>
              <MenuRoot>
                <MenuTrigger asChild>
                  <IconButton variant="ghost" color="inherit">
                    <BsThreeDotsVertical />
                  </IconButton>
                </MenuTrigger>
                <MenuContent minWidth="200px" width="full">
                <Button width="100%" variant="subtle" size="md" onClick={() => onClickPauseWorkorder({'workorder_id': item.workorder_id})} colorPalette="gray" display={
                    ['draft', 'done', 'cancel'].includes(item.production_state) || item.working_state == 'blocked' || !item.is_user_working? 'none' : 'flex'
                  }>Pausar</Button>
                              
                  <BlockWorkOrders item={item} />
                  
                  <Button width="100%" variant="solid" size="md" onClick={() => onClickUnblockWorkorder({'workorder_id': item.workorder_id})} colorPalette="red" display={
                    ['draft', 'done', 'cancel'].includes(item.production_state) || item.working_state != 'blocked'? 'none' : 'flex'
                  }>Desbloquear</Button>                
                </MenuContent>
              </MenuRoot>                
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
